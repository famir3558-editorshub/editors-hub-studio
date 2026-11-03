// Prints one line per image: "<file> x y w h" (pixels, origin top-left) for the largest face, or "<file> none".
import Foundation
import Vision
import AppKit
for path in CommandLine.arguments.dropFirst() {
    guard let img = NSImage(contentsOfFile: path), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { print("\(path) none"); continue }
    let W = Double(cg.width), H = Double(cg.height)
    let req = VNDetectFaceRectanglesRequest()
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    if let f = (req.results ?? []).max(by: { $0.boundingBox.width * $0.boundingBox.height < $1.boundingBox.width * $1.boundingBox.height }) {
        let b = f.boundingBox
        print(String(format: "%@ %.0f %.0f %.0f %.0f", path, b.minX * W, (1 - b.maxY) * H, b.width * W, b.height * H))
    } else { print("\(path) none") }
}
