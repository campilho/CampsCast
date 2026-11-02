// CampsCast — função do CloudFront para o site (viewer request).
//
// A origem é o endereço REST do S3, que só sabe entregar o objeto com o nome
// exato: o "Default root object" resolve a raiz, mas /estudio/ daria 403. Esta
// função completa o nome do index.html das pastas e leva /studio ao estúdio.
// Endereço com extensão (feed.xml, os MP3, imagens, estilos) passa intacto, e
// é por isso que ela não mexe no podcast.
//
// Onde colar: CloudFront → Functions → criar, colar este arquivo, publicar e
// associar à distribuição, no comportamento padrão, em "Viewer request".
// Escrita em ES5 para rodar em qualquer versão do runtime das funções. Testada
// no tests/smoke_test.sh.

function consulta(qs) {
  var partes = [];
  for (var k in qs) {
    var v = qs[k];
    var valores = v.multiValue ? v.multiValue : [v];
    for (var i = 0; i < valores.length; i++) {
      partes.push(k + (valores[i].value !== "" ? "=" + valores[i].value : ""));
    }
  }
  return partes.length ? "?" + partes.join("&") : "";
}

function redireciona(destino) {
  return { statusCode: 301, statusDescription: "Moved Permanently", headers: { location: { value: destino } } };
}

function handler(event) {
  var req = event.request;
  var uri = req.uri;
  if (uri === "/studio" || uri.indexOf("/studio/") === 0) {
    return redireciona("/estudio/" + consulta(req.querystring));
  }
  if (uri.charAt(uri.length - 1) === "/") {
    req.uri = uri + "index.html";
    return req;
  }
  var ultimo = uri.substring(uri.lastIndexOf("/") + 1);
  if (ultimo.indexOf(".") === -1) {
    return redireciona(uri + "/" + consulta(req.querystring));
  }
  return req;
}
