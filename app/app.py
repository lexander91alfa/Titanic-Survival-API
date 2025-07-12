# pages/3_📄_Documentação_API.py
import streamlit as st

st.set_page_config(page_title="Documentação da API", page_icon="📄", layout="wide")
st.title("📄 Documentação Interativa da API (Swagger UI)")

# A URL para o seu arquivo de especificação OpenAPI.
# Ela é construída a partir da URL base que você configurou.
openapi_url = f"{st.session_state.url}/openapi.yaml"

# Corpo do HTML que carrega e renderiza a interface do Swagger UI
# Ele usa uma CDN pública, então você não precisa de arquivos locais.
SWAGGER_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
        html {{ box-sizing: border-box; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        body {{ margin: 0; background: #fafafa; }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
    window.onload = function() {{
        const ui = SwaggerUIBundle({{
            // Ponto crucial: A URL para o seu arquivo de definição da API.
            url: "{openapi_url}",
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis
            ],
            // Configuração para permitir o envio da API Key
            // O usuário ainda precisará inseri-la manualmente na UI.
            onComplete: function() {{
                ui.preauthorizeApiKey("ApiKeyAuth", "{st.session_state.api_key}");
            }}
        }});
        window.ui = ui;
    }};
    </script>
</body>
</html>
"""

st.info(
    "Esta é uma visualização ao vivo da documentação da sua API. "
    "Você pode expandir os endpoints e testá-los diretamente daqui. "
    "A chave de API já foi pré-autorizada para sua conveniência."
)

# Renderiza o componente HTML no Streamlit
# O componente `st.html` é a forma moderna e segura de fazer isso.
st.html(SWAGGER_HTML, height=800, scrolling=True)