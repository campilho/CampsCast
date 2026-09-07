// Captura o microfone e imprime, por bloco, o nível total e o nível em duas
// bandas: graves (abaixo de 200 Hz, onde vivem avião, trânsito e TV atrás da
// parede) e voz (300 a 3400 Hz). Separar voz de ruído por nível é impossível;
// por banda é direto, e foi medido nas gravações do projeto:
//
//     voz de perto      razão voz-graves  -6,4 dB
//     avião passando                     -23,5 dB
//     moto na rua                        -38,3 dB
//
// A primeira linha da saída é "# <nome do dispositivo>", para o relatório dizer
// de qual microfone os números vieram.
//
// Existe porque a biblioteca padrão do Python não captura áudio e o projeto não
// admite dependência de pip ou brew. Compilado sob demanda por monitor.py.
import AVFoundation
import Foundation

/// Filtro de um polo. Encadeado duas vezes dá 12 dB por oitava, o bastante
/// para separar bandas largas.
struct UmPolo {
    let a: Float
    var z: Float = 0
    init(corte: Float, taxa: Float) { a = 1 - exp(-2 * .pi * corte / taxa) }
    mutating func passaBaixa(_ x: Float) -> Float { z += a * (x - z); return z }
}

let motor = AVAudioEngine()
let entrada = motor.inputNode
let formato = entrada.inputFormat(forBus: 0)
let taxa = Float(formato.sampleRate)
guard taxa > 0 else {
    FileHandle.standardError.write("microfone indisponível\n".data(using: .utf8)!)
    exit(1)
}

let nome = AVCaptureDevice.default(for: .audio)?.localizedName ?? "microfone padrão"
print("# \(nome) @ \(Int(taxa)) Hz")
fflush(stdout)

var grave1 = UmPolo(corte: 200, taxa: taxa), grave2 = UmPolo(corte: 200, taxa: taxa)
var vozAlta1 = UmPolo(corte: 300, taxa: taxa), vozAlta2 = UmPolo(corte: 300, taxa: taxa)
var vozBaixa1 = UmPolo(corte: 3400, taxa: taxa), vozBaixa2 = UmPolo(corte: 3400, taxa: taxa)

func decibeis(_ x: Float) -> Float { x > 0 ? 20 * log10(x) : -120 }

entrada.installTap(onBus: 0, bufferSize: AVAudioFrameCount(taxa / 20),
                   format: formato) { buffer, _ in
    guard let dados = buffer.floatChannelData?[0] else { return }
    let n = Int(buffer.frameLength)
    if n == 0 { return }
    var soma: Float = 0, somaGrave: Float = 0, somaVoz: Float = 0, pico: Float = 0
    for i in 0..<n {
        let x = dados[i]
        soma += x * x
        if abs(x) > pico { pico = abs(x) }

        let g = grave2.passaBaixa(grave1.passaBaixa(x))
        somaGrave += g * g

        // passa-alta = sinal menos a parte baixa; depois corta o topo
        let semGrave = x - vozAlta2.passaBaixa(vozAlta1.passaBaixa(x))
        let v = vozBaixa2.passaBaixa(vozBaixa1.passaBaixa(semGrave))
        somaVoz += v * v
    }
    let m = Float(n)
    print(String(format: "%.2f %.2f %.2f %.2f",
                 decibeis((soma / m).squareRoot()),
                 decibeis(pico),
                 decibeis((somaGrave / m).squareRoot()),
                 decibeis((somaVoz / m).squareRoot())))
    fflush(stdout)
}

do { try motor.start() } catch {
    FileHandle.standardError.write("erro ao abrir o microfone: \(error)\n".data(using: .utf8)!)
    exit(1)
}
RunLoop.main.run()
