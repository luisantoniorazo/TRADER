#!/bin/bash
#############################################
#  AlgoTrade X - Instalador Automático
#  Solo pega este comando en tu servidor
#############################################

set -e

SERVER_IP="188.166.35.189"
REPO_URL="https://github.com/luisantoniorazo/TRADER.git"
APP_DIR="/opt/algotrade"

echo ""
echo "============================================"
echo "  AlgoTrade X - Instalación Automática"
echo "  Servidor: $SERVER_IP"
echo "============================================"
echo ""

# ---- 1. Actualizar sistema ----
echo "[1/8] Actualizando sistema..."
apt update -y && apt upgrade -y
echo "OK"

# ---- 2. Instalar dependencias ----
echo "[2/8] Instalando Python, Git, Nginx, Curl..."
apt install -y python3 python3-pip python3-venv git curl nginx gnupg software-properties-common
echo "OK"

# ---- 3. Instalar Node.js 20 ----
echo "[3/8] Instalando Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi
npm install -g yarn
echo "Node: $(node -v) | Yarn: $(yarn -v)"

# ---- 4. Instalar MongoDB ----
echo "[4/8] Instalando MongoDB..."
if ! command -v mongod &> /dev/null; then
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg 2>/dev/null || true
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    apt update -y
    apt install -y mongodb-org
fi
systemctl start mongod
systemctl enable mongod
echo "MongoDB OK"

# ---- 5. Clonar repositorio ----
echo "[5/8] Descargando código de AlgoTrade X..."
rm -rf $APP_DIR
git clone $REPO_URL $APP_DIR
echo "Código descargado"

# ---- 6. Configurar Backend ----
echo "[6/8] Configurando Backend..."
cd $APP_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# Remove emergentintegrations if present (Emergent-internal package)
sed -i '/emergentintegrations/d' requirements.txt
pip install -r requirements.txt

cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=algotrade_db
CORS_ORIGINS=http://$SERVER_IP,https://$SERVER_IP
EOF

deactivate
echo "Backend configurado"

# ---- 7. Configurar Frontend ----
echo "[7/8] Configurando Frontend (esto toma unos minutos)..."
cd $APP_DIR/frontend

cat > .env << EOF
REACT_APP_BACKEND_URL=http://$SERVER_IP
EOF

yarn install --frozen-lockfile 2>/dev/null || yarn install
yarn build
echo "Frontend compilado"

# ---- 8. Configurar servicios ----
echo "[8/8] Configurando servicios del sistema..."

# Servicio backend (systemd)
cat > /etc/systemd/system/algotrade.service << EOF
[Unit]
Description=AlgoTrade X Backend
After=network.target mongod.service

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin:/usr/bin
ExecStart=$APP_DIR/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Nginx (proxy reverso)
cat > /etc/nginx/sites-available/algotrade << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    # Frontend
    location / {
        root $APP_DIR/frontend/build;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    # WebSocket
    location /api/ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOF

ln -sf /etc/nginx/sites-available/algotrade /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Arrancar todo
systemctl daemon-reload
systemctl enable algotrade
systemctl start algotrade
nginx -t && systemctl restart nginx

# ---- Verificar ----
echo ""
echo "============================================"
echo "  INSTALACION COMPLETADA!"
echo "============================================"
echo ""

# Verificar Binance
BINANCE_TEST=$(curl -s https://testnet.binance.vision/api/v3/ping)
if echo "$BINANCE_TEST" | grep -q "restricted"; then
    echo "  BINANCE: BLOQUEADO desde esta region"
else
    echo "  BINANCE: DISPONIBLE desde esta region"
fi

# Verificar Backend
BACKEND_TEST=$(curl -s http://localhost:8001/api/bot/status)
if echo "$BACKEND_TEST" | grep -q "is_running"; then
    echo "  BACKEND: FUNCIONANDO"
else
    echo "  BACKEND: ERROR - revisa con: journalctl -u algotrade -f"
fi

# Verificar Nginx
NGINX_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)
if [ "$NGINX_TEST" = "200" ]; then
    echo "  FRONTEND: FUNCIONANDO"
else
    echo "  FRONTEND: ERROR - revisa con: nginx -t"
fi

echo ""
echo "============================================"
echo "  ABRE TU NAVEGADOR EN:"
echo ""
echo "    http://$SERVER_IP"
echo ""
echo "  Ingresa tus API Keys de Binance y"
echo "  tu Token de Telegram, y listo!"
echo "============================================"
echo ""
