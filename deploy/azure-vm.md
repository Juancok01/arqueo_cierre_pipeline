# Máquina virtual en Azure

El tutor enciende una instancia EC2 en AWS para que el programa siga corriendo con el portátil apagado. Aquí ese papel lo hace una máquina virtual de Azure. El pipeline es el mismo: cada cinco minutos lee Supabase y, si hay un cierre nuevo, manda el correo.

Supabase se queda como está. Azure no reemplaza la base. Solo ejecuta el job.

## Qué se crea

| Pieza | Para qué |
|---|---|
| Grupo de recursos `rg-arqueo-cierres` | Junta la máquina y su disco para poder borrarlos juntos |
| Máquina `vm-arqueo-cierres` | Ubuntu, tamaño `Standard_B1s` |
| `cron` | Ejecuta `arqueo-cierres` cada cinco minutos |

`Standard_B1s` es el tamaño pequeño. Mientras exista, Azure cobra el tiempo que esté encendida. Con créditos de estudiante suele alcanzar. Si apagas y liberas la máquina, el cobro de cómputo se detiene.

## Crear la máquina

Hace falta [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) y una sesión iniciada:

```powershell
az login
az group create --name rg-arqueo-cierres --location eastus
az vm create --resource-group rg-arqueo-cierres --name vm-arqueo-cierres --image Ubuntu2404 --size Standard_B1s --admin-username azureuser --generate-ssh-keys --public-ip-sku Standard
```

El comando de la máquina imprime la IP pública. Con esa IP:

```powershell
scp -r C:\Users\juanc\OneDrive\Documents\Git\arqueo-cierre-pipeline azureuser@IP:~/
```

No copies `.venv` ni `data`. En la máquina, `.env` sí tiene que estar: contiene la URL de Supabase y la clave de Gmail, y no va al repositorio.

## Dentro de la máquina

```bash
ssh azureuser@IP
sudo apt update && sudo apt install -y python3-venv python3-pip
cd ~/arqueo-cierre-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
arqueo-cierres
```

La primera corrida debe decir que no hay cierres nuevos, o imprimir la simulación si `ENVIAR_CORREO=false`. Cuando el texto se vea bien, en `.env` pasa `ENVIAR_CORREO` a `true` y vacía `CORREO_PRUEBA` para que el aviso llegue al dueño.

Programa el job:

```bash
crontab -e
```

```cron
*/5 * * * * cd /home/azureuser/arqueo-cierre-pipeline && .venv/bin/arqueo-cierres >> /home/azureuser/arqueo-cierres.log 2>&1
```

`data/enviados.sqlite` vive en el disco de esa máquina. Si la borras, se olvida qué cierres ya avisó.
