// faces <image> [<image> ...]  ->  JSON {path: {"w":px,"h":px,"faces":[[x,y,w,h],...]}}  (normalised, origin top-left)
import Vision
import AppKit
var out: [String: Any] = [:]
for p in CommandLine.arguments.dropFirst() {
  guard let img = NSImage(contentsOf: URL(fileURLWithPath: p)), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { continue }
  let req = VNDetectFaceRectanglesRequest()
  try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
  var fs: [[Double]] = []
  for r in (req.results ?? []) {
    let b: CGRect = r.boundingBox
    let row: [Double] = [Double(b.minX), Double(1.0 - b.maxY), Double(b.width), Double(b.height)]
    fs.append(row)
  }
  out[p] = ["w": cg.width, "h": cg.height, "faces": fs]
}
print(String(data: try! JSONSerialization.data(withJSONObject: out), encoding: .utf8)!)
