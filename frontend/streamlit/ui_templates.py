import streamlit as st

def show_empty_state():
    """Renders a dashed card indicating that no images have been uploaded yet."""
    st.markdown(
        """
        <div style="text-align: center; padding: 40px 20px; background-color: #ffffff; border-radius: 8px; border: 1px dashed #0066cc; margin-top: 20px;">
            <h3 style="color: #003f7f; margin-top: 15px; margin-bottom: 5px;">Nenhuma imagem carregada</h3>
            <p style="color: #666666; max-width: 500px; margin: 0 auto 20px auto; font-size: 0.95rem;">
                Envie as fotos capturadas pelo drone para detectar automaticamente focos de lixo e gerar alertas de geolocalização.
            </p>
            <div style="font-size: 0.85rem; text-align: left; max-width: 400px; margin: 0 auto; color: #555555; background-color: #f8fbff; padding: 15px; border-radius: 6px;">
                <strong>Como começar:</strong>
                <ol style="margin-top: 5px; margin-bottom: 0; padding-left: 20px;">
                    <li>Arraste e solte ou clique para enviar imagens no painel acima.</li>
                    <li>Clique no botão <strong>"Classificar imagens"</strong>.</li>
                    <li>Acesse a aba <strong>"Alertas"</strong> para visualizar o mapa interativo.</li>
                </ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_card():
    """Renders the unauthenticated welcome login card."""
    st.markdown(
        """
        <div style="text-align: center; margin-top: 60px; padding: 40px 20px; background-color: #ffffff; border-radius: 12px; border: 1px solid rgba(0, 102, 204, 0.15); box-shadow: 0 4px 12px rgba(0, 63, 127, 0.05); max-width: 500px; margin-left: auto; margin-right: auto;">
            <h1 style="color: #003f7f; font-size: 2.5rem; margin-bottom: 10px; font-weight: 700;">🌊 SirenSky</h1>
            <p style="color: #555555; font-size: 1.05rem; margin-bottom: 30px;">
                Bem-vindo ao SirenSky. Acesse com sua conta Google para monitorar o processamento de imagens e alertas.
            </p>
        </div>
        </br>
        """,
        unsafe_allow_html=True
    )


def render_access_denied_card(email: str):
    """Renders an error card indicating that the user's email is not authorized."""
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 60px; padding: 40px 20px; background-color: #ffffff; border-radius: 12px; border: 1px solid #ef4444; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.05); max-width: 500px; margin-left: auto; margin-right: auto;">
            <h1 style="color: #b91c1c; font-size: 2.2rem; margin-bottom: 10px; font-weight: 700;">🚫 Acesso Negado</h1>
            <p style="color: #555555; font-size: 1.05rem; margin-bottom: 30px;">
                O e-mail <strong>{email}</strong> não está autorizado a acessar este painel. Entre em contato com o administrador.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_model_footer(model_name: str, margin_top: str = "60px"):
    """Renders a footer displaying the currently active classification model."""
    if model_name == "localmodel":
        model_display = "Modelo Local (Heurística de Tons de Cinza)"
    elif model_name == "debug":
        model_display = "Modelo de Debug (Simulado)"
    else:
        model_display = f"OpenAI API ({model_name})"

    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin-top: {margin_top};
            padding: 12px 24px;
            background: rgba(255, 255, 255, 0.75);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 8px;
            border: 1px solid rgba(0, 102, 204, 0.15);
            box-shadow: 0 4px 12px rgba(0, 63, 127, 0.05);
            font-size: 0.85rem;
            color: #003f7f;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        ">
            <span>Modelo Ativo:</span>
            <span style="
                background: linear-gradient(135deg, #0066cc 0%, #003f7f 100%);
                color: white;
                padding: 2px 10px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.75rem;
                letter-spacing: 0.5px;
                box-shadow: 0 2px 4px rgba(0, 63, 127, 0.15);
            ">{model_display}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
