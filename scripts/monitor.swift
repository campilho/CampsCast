// Captura o microfone e imprime nível em dBFS a cada bloco, uma linha por bloco.
// Existe porque a biblioteca padrão do Python não captura áudio, e o projeto não
// admite dependência instalada por pip ou brew. Compilado sob demanda por
// monitor.py com o swiftc que vem no Xcode.
import AVFoundation
import Foundation

let motor = AVAudioEngine()
let entrada = motor.inputNode
let formato = entrada.inputFormat(forBus: 0)
guard formato.sampleRate > 0 else {
    FileHandle.standardError.write("microfone indisponível\n".data(using: .utf8)!)
    exit(1)
}
let bloco = AVAudioFrameCount(formato.sampleRate / 20)   // ~50 ms

entrada.installTap(onBus: 0, bufferSize: bloco, format: formato) { buffer, _ in
    guard let dados = buffer.floatChannelData?[0] else { return }
    let n = Int(buffer.frameLength)
    if n == 0 { return }
    var soma: Float = 0
    var pico: Float = 0
    for i in 0..<n {
        let v = dados[i]
        soma += v * v
        if abs(v) > pico { pico = abs(v) }
    }
    let rms = (soma / Float(n)).squareRoot()
    let db = rms > 0 ? 20 * log10(rms) : -120
    let dbPico = pico > 0 ? 20 * log10(pico) : -120
    print(String(format: "%.2f %.2f", db, dbPico))
    fflush(stdout)
}

do {
    try motor.start()
} catch {
    FileHandle.standardError.write("erro ao abrir o microfone: \(error)\n".data(using: .utf8)!)
    exit(1)
}
RunLoop.main.run()
