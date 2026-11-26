import AppKit
for i in stride(from: 1, to: CommandLine.arguments.count, by: 2) {
 let input = CommandLine.arguments[i], output = CommandLine.arguments[i+1]
 guard let img=NSImage(contentsOfFile:input) else { fatalError("Unable to load SVG") }
 let size=img.size
 guard let rep=NSBitmapImageRep(bitmapDataPlanes:nil,pixelsWide:Int(size.width),pixelsHigh:Int(size.height),bitsPerSample:8,samplesPerPixel:4,hasAlpha:true,isPlanar:false,colorSpaceName:.deviceRGB,bytesPerRow:0,bitsPerPixel:0) else { fatalError("Unable to allocate bitmap") }
 NSGraphicsContext.saveGraphicsState()
 NSGraphicsContext.current=NSGraphicsContext(bitmapImageRep:rep)
 img.draw(in:NSRect(origin:.zero,size:size))
 NSGraphicsContext.restoreGraphicsState()
 try rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:output))
 print("Rendered \(output)")
}
