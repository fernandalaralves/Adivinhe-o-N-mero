# app.py
# Jogo "Adivinhe o Número" 


from flask import Flask, render_template_string, request, session, redirect, url_for, Response
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configurações do jogo
MIN_NUM = 1
MAX_NUM = 100

HTML_TEMPLATE = '''
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Adivinhe o Número</title>
  <link rel="stylesheet" href="{{ url_for('css') }}">
</head>
<body>
  <div class="card">
    <h1>Adivinhe o Número</h1>
    <p class="lead">Tente adivinhar um número entre <strong>{{ min_num }}</strong> e <strong>{{ max_num }}</strong>.</p>

    {% if message %}
      <div class="message {{ message_type }}">{{ message }}</div>
    {% endif %}

    {% if won %}
      <p>Você acertou em <strong>{{ attempts }}</strong> tentativa(s)!</p>
      <form method="post" action="{{ url_for('reset') }}">
        <button class="btn" type="submit">Jogar de novo</button>
      </form>
    {% else %}
      <form method="post" action="{{ url_for('guess') }}">
        <input autofocus name="guess" type="number" min="{{ min_num }}" max="{{ max_num }}" required placeholder="Seu palpite">
        <div class="controls">
          <button class="btn" type="submit">Enviar palpite</button>
          <a class="btn ghost" href="{{ url_for('reset') }}">Reiniciar jogo</a>
        </div>
      </form>
      <p class="small">Tentativas: <strong>{{ attempts }}</strong></p>
    {% endif %}

    <footer>
      <small>Segredo entre {{ min_num }} e {{ max_num }} — boa sorte! 🌟</small>
    </footer>
  </div>
</body>
</html>
'''

CSS_TEXT = '''
/* style.css - Estilo simples para o jogo */
*{box-sizing:border-box}
body{
  font-family: 'Nunito', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
  background: linear-gradient(135deg,#ffeef8 0%, #fff9f0 100%);
  margin:0;
  padding:40px 16px;
  display:flex;
  align-items:center;
  justify-content:center;
  min-height:100vh;
  color:#2b2b2b;
}
.card{
  width:100%;
  max-width:440px;
  background:linear-gradient(180deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9));
  border-radius:14px;
  padding:28px;
  box-shadow:0 10px 30px rgba(17,17,17,0.08);
  text-align:center;
}
h1{margin:0 0 8px;font-size:1.6rem}
.lead{margin:0 0 18px;color:#555}
input[type=number]{
  width:100%;
  padding:12px 14px;
  font-size:1rem;
  border-radius:8px;
  border:1px solid #e5d6e0;
  margin-bottom:12px;
}
.controls{display:flex;gap:8px;align-items:center;justify-content:center}
.btn{
  background:#ff4fa3;
  color:white;
  border:none;
  padding:10px 14px;
  border-radius:10px;
  cursor:pointer;
  font-weight:600;
  text-decoration:none;
}
.btn.ghost{background:transparent;color:#ff4fa3;border:1px solid rgba(255,79,163,0.15)}
.small{color:#777}
.message{padding:10px;border-radius:8px;margin-bottom:12px}
.message.hint{background:#fff7e6;border:1px solid #ffe5b2;color:#8a6d1a}
.message.error{background:#ffecec;border:1px solid #f5c6cb;color:#7a1e1e}
.message.success{background:#e8fff0;border:1px solid #c8f7d8;color:#145a2a}
footer{margin-top:16px}
'''


def start_new_game():
    session['secret'] = random.randint(MIN_NUM, MAX_NUM)
    session['attempts'] = 0
    session['won'] = False


@app.route('/')
def index():
    # Se não existir jogo ativo, cria um
    if 'secret' not in session:
        start_new_game()

    return render_template_string(HTML_TEMPLATE,
                                  min_num=MIN_NUM,
                                  max_num=MAX_NUM,
                                  message=None,
                                  message_type='',
                                  attempts=session.get('attempts', 0),
                                  won=session.get('won', False))


@app.route('/guess', methods=['POST'])
def guess():
    if 'secret' not in session:
        start_new_game()

    guess_raw = request.form.get('guess', '').strip()
    message = None
    message_type = ''

    # validação simples
    try:
        guess_val = int(guess_raw)
    except ValueError:
        message = 'Por favor, envie um número válido.'
        message_type = 'error'
        return render_template_string(HTML_TEMPLATE,
                                      min_num=MIN_NUM,
                                      max_num=MAX_NUM,
                                      message=message,
                                      message_type=message_type,
                                      attempts=session.get('attempts', 0),
                                      won=session.get('won', False))

    session['attempts'] = session.get('attempts', 0) + 1

    secret = session.get('secret')

    if guess_val == secret:
        session['won'] = True
        message = f'Parabéns! {guess_val} está correto!'
        message_type = 'success'
    elif guess_val < secret:
        message = 'Mais alto! 🔼'
        message_type = 'hint'
    else:
        message = 'Mais baixo! 🔽'
        message_type = 'hint'

    return render_template_string(HTML_TEMPLATE,
                                  min_num=MIN_NUM,
                                  max_num=MAX_NUM,
                                  message=message,
                                  message_type=message_type,
                                  attempts=session.get('attempts', 0),
                                  won=session.get('won', False))


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    start_new_game()
    return redirect(url_for('index'))


@app.route('/style.css')
def css():
    return Response(CSS_TEXT, mimetype='text/css')


if __name__ == '__main__':
    # Porta 5000 por padrão. Acesse http://127.0.0.1:5000
    app.run(debug=True)
