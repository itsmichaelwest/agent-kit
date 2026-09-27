#!/usr/bin/env python3
"""Build a local, timestamped frame-review artifact from a screen recording."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


FRAME_PATTERN = "frame-%06d.jpg"


def fail(message: str) -> None:
    raise SystemExit(message)


def run(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        fail(f"Required executable not found: {command[0]}")
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or "unknown error"
        fail(f"{command[0]} failed: {detail}")
    return result.stdout


def as_seconds(value: Any) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def timestamp_label(value: float | None) -> str:
    if value is None:
        return "missing"
    milliseconds = round(value * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def frame_timestamp(frame: dict[str, Any]) -> float | None:
    pts = as_seconds(frame.get("pts_time"))
    return pts if pts is not None else as_seconds(frame.get("best_effort_timestamp_time"))


def parse_rate(value: Any) -> float | None:
    try:
        numerator, denominator = str(value).split("/", 1)
        denominator_value = float(denominator)
        return float(numerator) / denominator_value if denominator_value else None
    except (AttributeError, TypeError, ValueError):
        return None


def probe_summary(video: Path) -> dict[str, Any]:
    raw = run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_streams", "-show_format", "-show_entries",
            "stream=codec_name,width,height,avg_frame_rate,r_frame_rate,time_base,nb_frames:stream_tags=rotate:stream_side_data=rotation:format=duration,format_name",
            "-of", "json", str(video),
        ]
    )
    data = json.loads(raw)
    if not data.get("streams"):
        fail("The recording has no decodable video stream.")
    stream = data["streams"][0]
    duration = as_seconds(data.get("format", {}).get("duration"))
    declared_count = stream.get("nb_frames")
    estimate = None
    estimate_basis = None
    if declared_count not in (None, "", "N/A"):
        try:
            estimate = int(declared_count)
            estimate_basis = "declared stream frame count"
        except ValueError:
            pass
    if estimate is None and duration is not None:
        rate = parse_rate(stream.get("avg_frame_rate"))
        if rate is not None:
            estimate = round(duration * rate)
            estimate_basis = "duration multiplied by declared average rate"
    rotation = stream.get("tags", {}).get("rotate")
    for side_data in stream.get("side_data_list", []):
        if side_data.get("rotation") is not None:
            rotation = side_data["rotation"]
    return {
        "source_file": video.name,
        "codec": stream.get("codec_name"),
        "encoded_width": stream.get("width"),
        "encoded_height": stream.get("height"),
        "duration_seconds": duration,
        "format": data.get("format", {}).get("format_name"),
        "declared_rate": stream.get("r_frame_rate"),
        "declared_average_rate": stream.get("avg_frame_rate"),
        "stream_time_base": stream.get("time_base"),
        "frame_count_estimate": estimate,
        "frame_count_estimate_basis": estimate_basis,
        "rotation_metadata_degrees": rotation,
    }


def probe(video: Path, start: float | None, duration: float | None) -> dict[str, Any]:
    raw = run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_streams", "-show_format", "-show_frames",
            "-show_entries",
            "stream=codec_name,width,height,avg_frame_rate,r_frame_rate,time_base,nb_frames:format=duration,format_name:frame=pts_time,best_effort_timestamp_time,pkt_dts_time,pkt_duration_time,pict_type,key_frame",
            "-of", "json", str(video),
        ]
    )
    data = json.loads(raw)
    if not data.get("streams"):
        fail("The recording has no decodable video stream.")
    if not data.get("frames"):
        fail("ffprobe returned no decoded video frames.")
    for index, frame in enumerate(data["frames"]):
        frame["_source_frame_index"] = index
    source_first_timestamp = next(
        (frame_timestamp(frame) for frame in data["frames"] if frame_timestamp(frame) is not None),
        None,
    )
    data["_source_first_timestamp"] = source_first_timestamp
    if start is not None and duration is not None:
        if source_first_timestamp is None:
            fail("The recording has no usable presentation timestamps for interval selection.")
        absolute_start = source_first_timestamp + start
        absolute_end = absolute_start + duration
        data["frames"] = [
            frame for frame in data["frames"]
            if (value := frame_timestamp(frame)) is not None and absolute_start <= value < absolute_end
        ]
        if not data["frames"]:
            fail(f"No decoded frames fall within the requested playback interval {start}-{start + duration} seconds.")
        source_indices = [frame["_source_frame_index"] for frame in data["frames"]]
        expected_indices = list(range(source_indices[0], source_indices[-1] + 1))
        if source_indices != expected_indices:
            fail("The requested timestamp interval is not a contiguous decoded-frame range.")
    return data


def extract(
    video: Path,
    destination: Path,
    thumbnail: bool,
    source_start_index: int | None,
    source_end_index: int | None,
) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    # Give the image muxer a synthetic, strictly increasing timeline. Original
    # presentation timestamps remain authoritative in frame-data.json.
    filters = []
    if source_start_index is not None and source_end_index is not None:
        filters.append(f"select='between(n,{source_start_index},{source_end_index})'")
    filters.append("setpts=N/TB")
    if thumbnail:
        filters.append("scale='min(320,iw)':-2")
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
            "-map", "0:v:0", "-vf", ",".join(filters),
            "-fps_mode", "passthrough", "-q:v", "5" if thumbnail else "2",
            str(destination / FRAME_PATTERN),
        ]
    )


def build_frame_data(
    probe_data: dict[str, Any],
    summary: dict[str, Any],
    video: Path,
    start: float | None,
    duration: float | None,
) -> dict[str, Any]:
    stream = probe_data["streams"][0]
    frames: list[dict[str, Any]] = []
    checks = {
        "fallback_count": 0,
        "missing_count": 0,
        "pts_best_effort_divergence_count": 0,
        "duplicate_count": 0,
        "non_monotonic_count": 0,
    }
    previous: float | None = None

    for index, source in enumerate(probe_data["frames"], start=1):
        pts = as_seconds(source.get("pts_time"))
        best_effort = as_seconds(source.get("best_effort_timestamp_time"))
        chosen = pts
        source_name = "pts_time"
        if chosen is None:
            chosen = best_effort
            source_name = "best_effort_timestamp_time"
            checks["fallback_count"] += 1
        if chosen is None:
            source_name = "missing"
            checks["missing_count"] += 1
        if pts is not None and best_effort is not None and abs(pts - best_effort) > 0.000001:
            checks["pts_best_effort_divergence_count"] += 1
        if chosen is not None and previous is not None:
            if chosen == previous:
                checks["duplicate_count"] += 1
            elif chosen < previous:
                checks["non_monotonic_count"] += 1
        if chosen is not None:
            previous = chosen
        frames.append(
            {
                "index": index,
                "source_frame_index": source.get("_source_frame_index", index - 1) + 1,
                "timestamp_seconds": chosen,
                "timestamp": timestamp_label(chosen),
                "timestamp_source": source_name,
                "pts_time": pts,
                "best_effort_timestamp_time": best_effort,
                "pkt_dts_time": as_seconds(source.get("pkt_dts_time")),
                "duration_seconds": as_seconds(source.get("pkt_duration_time")),
                "picture_type": source.get("pict_type"),
                "key_frame": bool(source.get("key_frame", 0)),
                "image": f"frames/frame-{index:06d}.jpg",
                "thumbnail": f"thumbnails/frame-{index:06d}.jpg",
            }
        )

    checks["selected_source"] = (
        "pts_time" if checks["fallback_count"] == 0
        else f"pts_time with {checks['fallback_count']} per-frame fallback(s)"
    )
    segment = None
    if start is not None and duration is not None:
        segment = {
            "requested_start_offset_seconds": start,
            "requested_duration_seconds": duration,
            "requested_end_offset_seconds": start + duration,
            "source_first_timestamp_seconds": probe_data.get("_source_first_timestamp"),
            "original_timestamp_offset_seconds": frames[0]["timestamp_seconds"],
            "first_frame_timestamp_seconds": frames[0]["timestamp_seconds"],
            "last_frame_timestamp_seconds": frames[-1]["timestamp_seconds"],
        }
    return {
        "schema_version": 1,
        "source_file": video.name,
        "video": {
            "codec": stream.get("codec_name"),
            "width": summary.get("encoded_width"),
            "height": summary.get("encoded_height"),
            "encoded_width": summary.get("encoded_width"),
            "encoded_height": summary.get("encoded_height"),
            "duration_seconds": summary.get("duration_seconds"),
            "format": summary.get("format"),
            "declared_rate": stream.get("r_frame_rate"),
            "declared_average_rate": stream.get("avg_frame_rate"),
            "stream_time_base": stream.get("time_base"),
            "frame_count_estimate": summary.get("frame_count_estimate"),
            "frame_count_estimate_basis": summary.get("frame_count_estimate_basis"),
            "rotation_metadata_degrees": summary.get("rotation_metadata_degrees"),
            "decoded_frame_count": len(frames),
        },
        "segment": segment,
        "timestamp_validation": checks,
        "frames": frames,
    }


def default_review() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "recording_context": {
            "build": "", "device_or_environment": "", "recording_method": "",
            "data_state": "", "scenario": "", "limitations": [],
        },
        "reviewed_ranges": [],
        "observations": [],
    }


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing artifact file: {path}")
    except json.JSONDecodeError as error:
        fail(f"Invalid JSON in {path}: {error}")
    if not isinstance(data, dict):
        fail(f"Expected a JSON object in {path}")
    return data


def image_geometry(path: Path) -> tuple[int, int]:
    raw = run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "json", str(path),
        ]
    )
    streams = json.loads(raw).get("streams", [])
    if not streams:
        fail(f"Could not read extracted frame geometry: {path}")
    return int(streams[0]["width"]), int(streams[0]["height"])


def reviewed_indices(review: dict[str, Any], frame_count: int) -> set[int]:
    reviewed: set[int] = set()
    ranges = review.get("reviewed_ranges", [])
    if not isinstance(ranges, list):
        fail("review.json reviewed_ranges must be an array.")
    for item in ranges:
        if not isinstance(item, dict):
            fail("Each reviewed range must be an object.")
        start, end = item.get("start_frame"), item.get("end_frame")
        if not isinstance(start, int) or not isinstance(end, int):
            fail("Reviewed ranges require integer start_frame and end_frame values.")
        if start < 1 or end < start or end > frame_count:
            fail(f"Invalid reviewed range {start}-{end}; valid frames are 1-{frame_count}.")
        reviewed.update(range(start, end + 1))
    return reviewed


def script_json(value: Any) -> str:
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            .replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e"))


def render_html(directory: Path, data: dict[str, Any], review: dict[str, Any], batch_size: int) -> None:
    frames = data.get("frames", [])
    if not isinstance(frames, list) or not frames:
        fail("frame-data.json contains no frames.")
    if batch_size < 1:
        fail("Batch size must be at least 1.")
    reviewed = reviewed_indices(review, len(frames))
    payload = {"data": data, "review": review, "reviewedCount": len(reviewed), "batchSize": batch_size}
    title = f"Screen recording review — {data.get('source_file', 'recording')}"
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><style>
:root{{color-scheme:light dark;font:15px/1.45 system-ui,sans-serif}}body{{margin:0;background:Canvas;color:CanvasText}}header,main{{width:min(1400px,calc(100% - 32px));margin:auto}}header{{padding:24px 0 8px}}h1,h2{{line-height:1.15}}.muted{{opacity:.65}}.notice{{padding:10px 12px;border:1px solid color-mix(in srgb,CanvasText 18%,transparent);border-radius:10px}}.viewer{{position:sticky;top:0;z-index:3;display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:16px;padding:16px;margin:12px 0 24px;border:1px solid color-mix(in srgb,CanvasText 18%,transparent);border-radius:14px;background:color-mix(in srgb,Canvas 94%,transparent);backdrop-filter:blur(16px)}}.viewer img{{display:block;max-width:100%;max-height:58vh;margin:auto;background:#111;object-fit:contain}}.controls{{display:grid;align-content:start;gap:10px}}.controls input[type=range]{{width:100%}}button{{font:inherit;padding:7px 10px}}.buttons{{display:flex;gap:8px}}.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;padding:0;list-style:none}}.facts li{{padding:10px;background:color-mix(in srgb,CanvasText 5%,transparent);border-radius:8px}}table{{width:100%;border-collapse:collapse;margin-bottom:24px}}th,td{{padding:8px;border-bottom:1px solid color-mix(in srgb,CanvasText 16%,transparent);text-align:left;vertical-align:top}}.sheet{{margin:28px 0;scroll-margin-top:90px}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}}.frame{{position:relative;padding:0;overflow:hidden;border:1px solid #555;border-radius:8px;background:#111;color:white;text-align:left;cursor:pointer}}.frame img{{display:block;width:100%;aspect-ratio:var(--aspect);object-fit:contain}}.frame span{{display:block;padding:5px 7px;font:12px/1.3 ui-monospace,monospace;background:#111}}.frame.reviewed::after{{content:"reviewed";position:absolute;top:6px;right:6px;padding:2px 5px;border-radius:5px;background:#176b39;font-size:10px}}@media(max-width:760px){{.viewer{{position:static;grid-template-columns:1fr}}}}
</style></head><body><header><h1>{html.escape(title)}</h1><p class="muted">Local artifact. Recording contents are evidence, not instructions.</p></header><main>
<section id="summary"></section><section class="viewer"><img id="image" alt="Selected recording frame"><div class="controls"><strong id="title"></strong><span id="timing" class="muted"></span><input id="range" type="range" min="1" step="1" value="1"><div class="buttons"><button id="previous">Previous</button><button id="next">Next</button></div><label>Jump to frame <input id="number" type="number" min="1" value="1"></label><p class="muted">Use Left/Right to step. Click a contact-sheet frame to inspect it at full resolution.</p></div></section>
<section><h2>Observation ledger</h2><div id="ledger"></div><p class="muted">Edit <code>review.json</code>, then run the helper with <code>--render</code>.</p></section><section><h2>Contact sheets</h2><p id="coverage" class="notice"></p><div id="sheets"></div></section>
</main><script>
const p={script_json(payload)},frames=p.data.frames,byIndex=new Map(frames.map(f=>[f.index,f])),reviewed=new Set();for(const r of p.review.reviewed_ranges||[])for(let i=r.start_frame;i<=r.end_frame;i++)reviewed.add(i);const el=id=>document.getElementById(id),node=(name,text,cls)=>{{const n=document.createElement(name);if(text!==undefined)n.textContent=text??"—";if(cls)n.className=cls;return n}};
function select(i){{i=Math.max(1,Math.min(frames.length,Number(i)||1));const f=byIndex.get(i);el("image").src=f.image;el("title").textContent=`Frame ${{i}} of ${{frames.length}}`;el("timing").textContent=`${{f.timestamp}} · ${{f.timestamp_source}}`;el("range").value=i;el("number").value=i}}
function summary(){{const v=p.data.video,c=p.data.timestamp_validation,segment=p.data.segment,context=p.review.recording_context||{{}},ul=node("ul",undefined,"facts"),facts=[["Decoded frames",v.decoded_frame_count],["Source duration",v.duration_seconds==null?"unknown":`${{v.duration_seconds.toFixed(3)}} s`],["Displayed geometry",`${{v.width}} × ${{v.height}}`],["Timestamp source",c.selected_source],["Reviewed coverage",`${{p.reviewedCount}} / ${{frames.length}} frames`],["Declared rates",`${{v.declared_rate||"unknown"}}; average ${{v.declared_average_rate||"unknown"}}`],["Preflight frame estimate",v.frame_count_estimate==null?"unavailable":`${{v.frame_count_estimate}} · ${{v.frame_count_estimate_basis}}`]],contextFacts=[["Build",context.build],["Device or environment",context.device_or_environment],["Recording method",context.recording_method],["Data state",context.data_state],["Scenario",context.scenario],["Limitations",Array.isArray(context.limitations)?context.limitations.join("; "):context.limitations]].filter(([,value])=>value);if(v.width!==v.encoded_width||v.height!==v.encoded_height)facts.push(["Encoded geometry",`${{v.encoded_width}} × ${{v.encoded_height}} · rotation metadata ${{v.rotation_metadata_degrees??"unknown"}}°`]);if(segment)facts.push(["Selected interval",`${{segment.requested_start_offset_seconds}}–${{segment.requested_end_offset_seconds}} s from playback start · first original PTS ${{segment.original_timestamp_offset_seconds}} s`]);for(const [a,b]of facts){{const li=node("li");li.append(node("strong",a),document.createElement("br"),document.createTextNode(b));ul.append(li)}}el("summary").append(ul);if(contextFacts.length){{const contextList=node("ul",undefined,"facts");for(const [a,b]of contextFacts){{const li=node("li");li.append(node("strong",a),document.createElement("br"),document.createTextNode(b));contextList.append(li)}}el("summary").append(node("h2","Recording context"),contextList)}}el("summary").append(node("p",`Timestamp checks: ${{c.duplicate_count}} duplicate, ${{c.non_monotonic_count}} non-monotonic, ${{c.missing_count}} missing, ${{c.pts_best_effort_divergence_count}} PTS/best-effort divergent. Declared recording rates are metadata, not measured application FPS.`,"notice"))}}
function ledger(){{const items=p.review.observations||[],host=el("ledger");if(!items.length){{host.append(node("p","No observations recorded yet.","notice"));return}}const table=node("table"),head=node("tr");for(const x of["Frames and time","Visible observation","User impact","Proposed improvement","Risk","Evidence","Confidence"])head.append(node("th",x));table.append(head);for(const item of items){{const a=byIndex.get(item.start_frame),b=byIndex.get(item.end_frame||item.start_frame),row=node("tr"),range=a&&b?`F${{a.index}}–F${{b.index}} · ${{a.timestamp}}–${{b.timestamp}}`:"invalid frame range",refs=Array.isArray(item.source_references)?item.source_references.join("; "):item.source_references,evidence=[item.evidence_level,refs,item.validation_needed].filter(Boolean).join(" · ");for(const x of[range,item.observation,item.user_impact,item.proposed_improvement,item.regression_risk,evidence,item.confidence])row.append(node("td",x));table.append(row)}}host.append(table)}}
function sheets(){{el("coverage").textContent=`${{p.reviewedCount}} of ${{frames.length}} decoded frames are explicitly marked reviewed. Generated contact sheets do not count as review coverage.`;for(let o=0;o<frames.length;o+=p.batchSize){{const batch=frames.slice(o,o+p.batchSize),section=node("section",undefined,"sheet"),grid=node("div",undefined,"grid");section.append(node("h3",`Frames ${{batch[0].index}}–${{batch.at(-1).index}} · ${{batch[0].timestamp}}–${{batch.at(-1).timestamp}}`));for(const f of batch){{const button=node("button",undefined,`frame${{reviewed.has(f.index)?" reviewed":""}}`),image=node("img");button.type="button";button.style.setProperty("--aspect",`${{p.data.video.width}} / ${{p.data.video.height}}`);image.src=f.thumbnail;image.loading="lazy";image.alt=`Frame ${{f.index}}`;button.append(image,node("span",`F${{f.index}} · ${{f.timestamp}}`));button.onclick=()=>{{select(f.index);scrollTo({{top:0,behavior:"smooth"}})}};grid.append(button)}}section.append(grid);el("sheets").append(section)}}}}
el("range").max=frames.length;el("number").max=frames.length;el("range").oninput=e=>select(e.target.value);el("number").onchange=e=>select(e.target.value);el("previous").onclick=()=>select(+el("range").value-1);el("next").onclick=()=>select(+el("range").value+1);document.onkeydown=e=>{{if(e.target.matches("input"))return;if(e.key==="ArrowLeft")select(+el("range").value-1);if(e.key==="ArrowRight")select(+el("range").value+1)}};summary();ledger();sheets();select(1);
</script></body></html>"""
    (directory / "index.html").write_text(document, encoding="utf-8")


def validate_extraction(directory: Path, expected: int) -> None:
    full = len(list((directory / "frames").glob("frame-*.jpg")))
    thumbs = len(list((directory / "thumbnails").glob("frame-*.jpg")))
    if full != expected or thumbs != expected:
        fail(f"Frame-count validation failed: ffprobe={expected}, full-resolution={full}, thumbnails={thumbs}")


def build(
    video: Path,
    output: Path,
    batch_size: int,
    start: float | None,
    duration: float | None,
) -> None:
    if not video.is_file():
        fail(f"Recording not found: {video}")
    if output.exists():
        if not output.is_dir():
            fail(f"Output path is not a directory: {output}")
        if any(output.iterdir()):
            fail(f"Output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    summary = probe_summary(video)
    probed = probe(video, start, duration)
    data = build_frame_data(probed, summary, video, start, duration)
    source_start = probed["frames"][0]["_source_frame_index"] if start is not None else None
    source_end = probed["frames"][-1]["_source_frame_index"] if start is not None else None
    extract(video, output / "frames", thumbnail=False,
            source_start_index=source_start, source_end_index=source_end)
    extract(video, output / "thumbnails", thumbnail=True,
            source_start_index=source_start, source_end_index=source_end)
    validate_extraction(output, len(data["frames"]))
    width, height = image_geometry(output / data["frames"][0]["image"])
    data["video"]["width"] = width
    data["video"]["height"] = height
    (output / "frame-data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    review = default_review()
    (output / "review.json").write_text(json.dumps(review, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    render_html(output, data, review, batch_size)


def rerender(directory: Path, batch_size: int) -> None:
    data = load_json(directory / "frame-data.json")
    review = load_json(directory / "review.json")
    validate_extraction(directory, len(data.get("frames", [])))
    render_html(directory, data, review, batch_size)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recording", nargs="?", help="Path to the screen recording")
    parser.add_argument("--output", type=Path, help="Empty output directory; defaults to a temporary directory")
    parser.add_argument("--render", type=Path, metavar="ARTIFACT_DIR", help="Rebuild HTML from an existing artifact")
    parser.add_argument("--probe-only", action="store_true", help="Print recording metadata without extracting frames")
    parser.add_argument("--start", type=float, help="Seconds from playback start at which to begin extraction")
    parser.add_argument("--duration", type=float, help="Duration of one bounded extraction interval")
    parser.add_argument("--batch-size", type=int, default=24, help="Frames per contact-sheet batch")
    args = parser.parse_args()
    if bool(args.recording) == bool(args.render):
        parser.error("provide either a recording path or --render ARTIFACT_DIR")
    if args.render and args.output:
        parser.error("--output cannot be used with --render")
    if (args.start is None) != (args.duration is None):
        parser.error("--start and --duration must be supplied together")
    if args.start is not None and args.start < 0:
        parser.error("--start cannot be negative")
    if args.duration is not None and args.duration <= 0:
        parser.error("--duration must be greater than zero")
    if args.render and (args.probe_only or args.start is not None):
        parser.error("--probe-only, --start, and --duration cannot be used with --render")
    if args.probe_only and args.output:
        parser.error("--output cannot be used with --probe-only")
    if args.render:
        directory = args.render.expanduser().resolve()
        rerender(directory, args.batch_size)
    else:
        required = ("ffprobe",) if args.probe_only else ("ffmpeg", "ffprobe")
        for executable in required:
            if shutil.which(executable) is None:
                fail(f"Required executable not found: {executable}")
        video = Path(args.recording).expanduser().resolve()
        if not video.is_file():
            fail(f"Recording not found: {video}")
        if args.probe_only:
            print(json.dumps(probe_summary(video), indent=2))
            return
        directory = (args.output.expanduser().resolve() if args.output
                     else Path(tempfile.mkdtemp(prefix="screen-recording-review-")))
        build(video, directory, args.batch_size, args.start, args.duration)
    print(directory / "index.html")


if __name__ == "__main__":
    main()
