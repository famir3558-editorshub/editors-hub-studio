import Vision; import AVFoundation
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let asset = AVAsset(url: url)
let track = asset.tracks(withMediaType: .video)[0]
let reader = try! AVAssetReader(asset: asset)
let out = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
reader.add(out); reader.startReading()
func mid(_ r: VNFaceLandmarkRegion2D?) -> (Double, Double, Double, Double)? {
  guard let p = r?.normalizedPoints, p.count > 0 else { return nil }
  let xs = p.map{Double($0.x)}, ys = p.map{Double($0.y)}
  return (xs.reduce(0,+)/Double(p.count), ys.reduce(0,+)/Double(p.count), ys.max()!-ys.min()!, xs.max()!-xs.min()!)
}
while let sb = out.copyNextSampleBuffer() {
  guard let pb = CMSampleBufferGetImageBuffer(sb) else { continue }
  let t = CMSampleBufferGetPresentationTimeStamp(sb).seconds
  let req = VNDetectFaceLandmarksRequest()
  try? VNImageRequestHandler(cvPixelBuffer: pb).perform([req])
  guard let f = (req.results ?? []).max(by: {$0.boundingBox.width < $1.boundingBox.width}) else { print(String(format:"%.2f none", t)); continue }
  let b = f.boundingBox
  var eyeOpen = -1.0, pupY = -9.0
  if let le = mid(f.landmarks?.leftEye), let re = mid(f.landmarks?.rightEye) {
    eyeOpen = (le.2/le.3 + re.2/re.3)/2
    if let lp = mid(f.landmarks?.leftPupil), let rp = mid(f.landmarks?.rightPupil) {
      pupY = ((lp.1-le.1)/le.3 + (rp.1-re.1)/re.3)/2
    }
  }
  print(String(format:"%.2f %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f", t, b.midX, 1-b.midY, b.height, f.pitch?.doubleValue ?? 9, f.yaw?.doubleValue ?? 9, f.roll?.doubleValue ?? 9, eyeOpen, pupY))
}
