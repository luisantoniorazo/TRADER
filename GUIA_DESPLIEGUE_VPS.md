# Guía de Despliegue - AlgoTrade X en VPS

## Requisitos Previos
- Un VPS con Ubuntu 22.04+ (DigitalOcean, Hetzner, Linode, Vultr, etc.)
- Mínimo: 1 vCPU, 1GB RAM, 20GB disco
- Una región donde Binance NO esté bloqueado (Europa, Asia funcionan bien. USA está restringido)
- Dominio (opcional, pero recomendado para HTTPS)

---

## Paso 1: Guardar el código en Github

1. En el chat de Emergent, haz clic en **"Save to Github"** (ícono de Git en la barra de entrada)
2. Conecta tu cuenta de Github si no lo has hecho
3. Se creará un repositorio con todo el código

---

## Paso 2: Crear tu VPS

### Opción recomendada: DigitalOcean ($6/mes)
1. Ve a https://www.digitalocean.com
2. Crea un Droplet:
   - **Región**: Amsterdam, Frankfurt, o Singapore (NO USA)
   - **Imagen**: Ubuntu 24.04
   - **Plan**: Basic $6/mes (1 vCPU, 1GB RAM)
   - **Autenticación**: SSH key (recomendado) o contraseña

### Opción económica: Hetzner (~$4/mes)
1. Ve a https://www.hetzner.com/cloud
2. Mismo proceso, región: Nuremberg o Helsinki

---

## Paso 3: Configurar el servidor

Conéctate por SSH:
```bash
ssh root@TU_IP_DEL_SERVIDOR
```

### Instalar dependencias del sistema:
```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar Python, Node.js, MongoDB, Nginx, Git
apt install -y python3 python3-pip python3-venv git curl nginx certbot python3-certbot-nginx

# Instalar Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Instalar yarn
npm install -g yarn

# Instalar MongoDB
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt update
apt install -y mongodb-org
systemctl start mongod
systemctl enable mongod
```

---

## Paso 4: Clonar y configurar el proyecto

```bash
# Clonar tu repositorio
cd /opt
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git algotrade
cd algotrade

# Crear entorno virtual de Python
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar variables de entorno del backend
cat > .env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=algotrade_db
CORS_ORIGINS=https://tudominio.com,http://TU_IP_DEL_SERVIDOR
EOF

# Instalar dependencias del frontend
cd ../frontend

# Configurar variables de entorno del frontend
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=http://TU_IP_DEL_SERVIDOR
EOF

yarn install
yarn build
```

---

## Paso 5: Configurar servicios con systemd

### Backend (FastAPI):
```bash
cat > /etc/systemd/system/algotrade-backend.service << 'EOF'
[Unit]
Description=AlgoTrade X Backend
After=network.target mongod.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/algotrade/backend
Environment=PATH=/opt/algotrade/backend/venv/bin
ExecStart=/opt/algotrade/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

### Activar y arrancar:
```bash
systemctl daemon-reload
systemctl enable algotrade-backend
systemctl start algotrade-backend

# Verificar que funciona:
systemctl status algotrade-backend
curl http://localhost:8001/api/bot/status
```

---

## Paso 6: Configurar Nginx (proxy reverso)

```bash
cat > /etc/nginx/sites-available/algotrade << 'EOF'
server {
    listen 80;
    server_name TU_IP_DEL_SERVIDOR;  # o tudominio.com si tienes dominio

    # Frontend (archivos estáticos del build de React)
    location / {
        root /opt/algotrade/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    # WebSocket
    location /api/ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
EOF

# Activar el sitio
ln -sf /etc/nginx/sites-available/algotrade /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```

---

## Paso 7: HTTPS con Let's Encrypt (si tienes dominio)

```bash
# Solo si tienes un dominio apuntando a tu IP
certbot --nginx -d tudominio.com
```

---

## Paso 8: Verificar que todo funciona

```bash
# 1. Verificar MongoDB
mongosh --eval "db.runCommand({ping:1})"

# 2. Verificar Backend
curl http://localhost:8001/api/bot/status

# 3. Verificar que Binance NO está bloqueado desde tu VPS
curl -s https://testnet.binance.vision/api/v3/ping
# Debería devolver: {} (vacío = OK)
# Si devuelve "restricted location" = necesitas otro servidor/región

# 4. Abrir en el navegador
# http://TU_IP_DEL_SERVIDOR (o https://tudominio.com)
```

---

## Paso 9: Configurar la app

1. Abre la app en tu navegador
2. Ingresa tus API Keys de Binance Testnet
3. Ingresa tu Token y Chat ID de Telegram
4. Haz clic en "CONFIGURAR Y CONTINUAR"
5. Haz clic en "INICIAR BOT"
6. El bot empezará a analizar las 30 criptomonedas y ejecutar trades

---

## Comandos útiles de mantenimiento

```bash
# Ver logs del bot en tiempo real
journalctl -u algotrade-backend -f

# Reiniciar el bot
systemctl restart algotrade-backend

# Actualizar código desde Github
cd /opt/algotrade
git pull
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && yarn install && yarn build
systemctl restart algotrade-backend
systemctl restart nginx
```

---

## Pasar de Testnet a Producción Real

Cuando estés listo para operar con dinero real:

1. Genera API Keys en tu cuenta real de Binance (binance.com > API Management)
2. Activa permisos de "Enable Spot & Margin Trading"
3. Restringe las IPs a solo la IP de tu VPS (seguridad)
4. En la app, desmarca "TESTNET MODE" al configurar
5. Deposita USDT en tu cuenta de Binance

**IMPORTANTE:** Empieza con poco dinero para probar. El trading automatizado conlleva riesgos.

---

## Costos estimados mensuales
| Concepto | Costo |
|----------|-------|
| VPS (DigitalOcean/Hetzner) | $4-6/mes |
| Dominio (opcional) | $10/año |
| Binance | Sin costo (comisiones por trade: 0.1%) |
| Telegram | Gratis |
| **Total** | **~$6/mes** |
