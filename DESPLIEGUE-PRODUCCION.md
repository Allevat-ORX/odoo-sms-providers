# 🚀 Despliegue en Producción - Módulos SMS Odoo 18

## 📋 Servidores de Destino

### 1. **AWS OnRentX** (Producción)
- URL: [A configurar]
- Base de datos: [A configurar]
- Usuario: admin

### 2. **AWS Trama** (Producción)
- URL: [A configurar]
- Base de datos: [A configurar]
- Usuario: admin

### 3. **VM .140** (Pruebas Aleix)
- URL: http://192.168.0.140:8069
- Base de datos: onrentx_test
- Usuario: linux-odoo
- SSH: `ssh linux-odoo@192.168.0.140` (password: odooserver)

---

## ✅ Estado Actual

**Módulos probados y funcionando en:**
- ✅ VM .80 (odoo.tramarental.com)
- ✅ Base de datos: ORX
- ✅ Zadarma: Funcionando 100%
- ✅ LabsMobile: Funcionando 100%

**Credenciales configuradas:**
- Zadarma User Key: `80d3fa87f5c59e7f`
- Zadarma Secret Key: `fc8e10c06e5c3b8a`
- LabsMobile Username: `allevat@onrentx.com`
- LabsMobile Token: `fVRFqQHD2vaPnuWJMwu3KTEAdGTvWpO3`

---

## 📦 INSTALACIÓN PASO A PASO

### Paso 1: Preparar Repositorio
```bash
# Asegurarse de tener la última versión
cd /home/aleix/Proyectos-Claude/Zadarma-MCP/odoo-module/sms_zadarma_v2
git pull origin master
```

### Paso 2: Instalar en VM .140 (Aleix)

```bash
# Conectar a VM
ssh linux-odoo@192.168.0.140

# 1. Instalar dependencia OCA
cd /tmp
git clone -b 18.0 https://github.com/OCA/server-tools.git
sudo cp -r server-tools/iap_alternative_provider /opt/odoo/addons/
sudo chown -R odoo:odoo /opt/odoo/addons/iap_alternative_provider

# 2. Clonar módulos SMS
cd /opt/odoo/addons/
sudo git clone https://github.com/Allevat-ORX/odoo-sms-providers.git
sudo chown -R odoo:odoo odoo-sms-providers/

# 3. Reiniciar Odoo
echo 'odooserver' | sudo -S systemctl restart odoo

# 4. Verificar logs
tail -f /var/log/odoo/odoo.log
```

**Desde interfaz Odoo (http://192.168.0.140:8069):**
```
1. Apps → Update Apps List
2. Buscar "IAP Alternative Provider" → Instalar
3. Buscar "Zadarma SMS Connector" → Instalar
4. Buscar "LabsMobile SMS Connector" → Instalar
```

**Configurar credenciales:**
```
Settings → Technical → IAP → Accounts

Para Zadarma:
- Service: SMS
- Provider: Zadarma
- User Key: 80d3fa87f5c59e7f
- Secret Key: fc8e10c06e5c3b8a
- Test Connection

Para LabsMobile:
- Service: SMS
- Provider: LabsMobile
- Username: allevat@onrentx.com
- API Token: fVRFqQHD2vaPnuWJMwu3KTEAdGTvWpO3
- Test Connection
```

### Paso 3: Instalar en AWS OnRentX

**Primero obtener acceso SSH al servidor AWS:**
```bash
# Conectar al servidor AWS OnRentX
ssh [usuario]@[ip_servidor_onrentx]
```

**Luego seguir los mismos pasos del Paso 2:**
1. Instalar iap_alternative_provider
2. Clonar odoo-sms-providers
3. Instalar módulos desde interfaz
4. Configurar credenciales

### Paso 4: Instalar en AWS Trama

```bash
# Conectar al servidor AWS Trama
ssh [usuario]@[ip_servidor_trama]
```

**Luego seguir los mismos pasos del Paso 2:**
1. Instalar iap_alternative_provider
2. Clonar odoo-sms-providers
3. Instalar módulos desde interfaz
4. Configurar credenciales

---

## 🧪 PRUEBAS POST-INSTALACIÓN

### Script de Prueba Python (XML-RPC)

Crear archivo `/tmp/test_sms.py` en cada servidor:

```python
#!/usr/bin/env python3
import xmlrpc.client

# CONFIGURAR ESTOS VALORES PARA CADA SERVIDOR
url = "https://tu-odoo.com"  # URL del servidor
db = "tu_base_datos"
username = "admin"
password = "tu_password"
numero_prueba = "+5214424751707"  # Número de prueba

print("=" * 70)
print(f"📨 PROBANDO SMS EN {url}")
print("=" * 70)

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Test Zadarma
print("\n🔵 Test 1: Zadarma")
sms_id = models.execute_kw(db, uid, password,
    'sms.sms', 'create',
    [{
        'number': numero_prueba,
        'body': f'Test Zadarma desde {db} - Funcionando OK'
    }])
print(f"✅ SMS creado (ID: {sms_id})")

# Test LabsMobile
print("\n🟢 Test 2: LabsMobile")
sms_id = models.execute_kw(db, uid, password,
    'sms.sms', 'create',
    [{
        'number': numero_prueba,
        'body': f'Test LabsMobile desde {db} - Funcionando OK'
    }])
print(f"✅ SMS creado (ID: {sms_id})")

print("\n" + "=" * 70)
print("✅ Pruebas completadas. Verificar celular.")
print("=" * 70)
```

**Ejecutar en cada servidor:**
```bash
python3 /tmp/test_sms.py
```

---

## 📊 CHECKLIST DE INSTALACIÓN

### VM .140 (Aleix)
- [ ] iap_alternative_provider instalado
- [ ] odoo-sms-providers clonado
- [ ] Módulos instalados desde interfaz
- [ ] Zadarma configurado
- [ ] LabsMobile configurado
- [ ] Test Connection exitoso (ambos)
- [ ] SMS de prueba enviados y recibidos

### AWS OnRentX
- [ ] iap_alternative_provider instalado
- [ ] odoo-sms-providers clonado
- [ ] Módulos instalados desde interfaz
- [ ] Zadarma configurado
- [ ] LabsMobile configurado
- [ ] Test Connection exitoso (ambos)
- [ ] SMS de prueba enviados y recibidos

### AWS Trama
- [ ] iap_alternative_provider instalado
- [ ] odoo-sms-providers clonado
- [ ] Módulos instalados desde interfaz
- [ ] Zadarma configurado
- [ ] LabsMobile configurado
- [ ] Test Connection exitoso (ambos)
- [ ] SMS de prueba enviados y recibidos

---

## 🆘 Troubleshooting Común

### Módulo no aparece en Apps
```bash
# Verificar permisos
sudo chown -R odoo:odoo /opt/odoo/addons/odoo-sms-providers/

# Reiniciar Odoo
sudo systemctl restart odoo

# En interfaz: Apps → Update Apps List
```

### Error al conectar con API
- Verificar credenciales copiadas correctamente
- No debe haber espacios al inicio/final
- Probar Test Connection en IAP Account

### SMS no llega
1. Verificar formato número: `+5214424751707` (debe incluir `+`)
2. Verificar balance en cuenta del proveedor
3. Revisar logs: `tail -f /var/log/odoo/odoo.log`

---

## 💰 Costos y Saldos

### Zadarma
- Balance actual: [Verificar en panel]
- Costo por SMS: ~$0.075 USD
- Panel: https://zadarma.com

### LabsMobile
- Balance actual: ~1 crédito
- Costo por SMS: Variable (más económico que Zadarma)
- Panel: https://www.labsmobile.com

**Recomendación:** Recargar saldo si balance < 50 créditos

---

## 📞 Contacto / Soporte

**Desarrollador:** Aleix - OnRentX
**Email:** allevat@onrentx.com
**GitHub:** https://github.com/Allevat-ORX/odoo-sms-providers

**En caso de problemas:**
1. Revisar logs de Odoo primero
2. Verificar credenciales en panel del proveedor
3. Probar API directamente con curl/python
4. Contactar a Aleix con logs completos

---

## 📝 Notas Finales

- Ambos módulos usan las **mismas credenciales** en todos los servidores
- Se puede cambiar de proveedor sin reiniciar Odoo
- Los SMS se registran en el log de Odoo para auditoría
- Credenciales se almacenan encriptadas en base de datos

---

**Fecha de preparación:** 5 de Noviembre, 2025
**Versión módulos:** 1.0.0
**Odoo:** 18.0
**Status:** ✅ Listo para despliegue
