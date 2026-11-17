"""
Seed Idempotente dos Sistemas Mapeados do HC-UFPE (USID)
========================================================
Cadastra e mantém sincronizadas no banco local (data/app.db) as aplicações
levantadas na planilha e validadas via SSH/HTTP/TCP.
"""

import json
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.aplicacao import Aplicacao


def get_seed_applications_data() -> List[Dict[str, Any]]:
    """Retorna a definição dos 14 registros de monitoramento para os 13 sistemas."""
    return [
        {
            "nome": "UTI Manager",
            "descricao": "Gestão e reserva de leitos de UTI (Reserva UTI)",
            "url_base": "https://10.34.0.192",
            "possui_rota_health": True,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": True,
            "zabbix_host_id": "HC-UFPE-VP-SAT-UTI",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "uti",
            "http_headers": None,
            "bancos_adicionais": None,
            "servicos_monitorados": json.dumps({
                "systemd": ["hc-uti"],
                "containers": ["hc-uti-backend", "hc-uti-nginx"],
            }),
        },
        {
            "nome": "Quimo",
            "descricao": "Agendamento e gestão de quimioterapia",
            "url_base": "https://10.34.0.191",
            "possui_rota_health": True,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": None,
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "quimo",
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "PostgreSQL Quimo", "host": "10.34.0.191", "porta": 5432},
            ]),
            "servicos_monitorados": json.dumps({
                "systemd": ["nginx"],
                "containers": ["quimio_app", "quimio_db_app"],
            }),
        },
        {
            "nome": "Escala de MEWS",
            "descricao": "Escala clínica de alerta precoce (CINCO HC)",
            "url_base": "https://10.34.0.197/login",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": False,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": None,
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "mews",
            "http_headers": None,
            "bancos_adicionais": None,
            "servicos_monitorados": json.dumps({
                "containers": ["cinco_hc-nginx-1", "cinco_hc-app-1", "cinco_hc-postgres-1"],
            }),
        },
        {
            "nome": "Wokibi",
            "descricao": "IA e anonimização para dados de hemodiálise",
            "url_base": "http://10.34.0.219:8080",
            "possui_rota_health": True,
            "url_health": "/health",
            "possui_banco_aghu": False,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": None,
            "criticidade": "MEDIA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "wokibi",
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "MongoDB Wokibi", "host": "10.34.0.219", "porta": 27017},
            ]),
            "servicos_monitorados": json.dumps({
                "containers": ["wokibi-mongodb"],
                "processes": ["app_anony.py", "next-server"],
                "extra_http": [{"nome": "Frontend Next.js", "url": "http://10.34.0.219:3000/"}],
            }),
        },
        {
            "nome": "Gestão interna da LEC",
            "descricao": "Comunicação cirúrgica e gestão interna da lista de espera",
            "url_base": "https://10.34.0.202",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": None,
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "lec",
            "http_headers": None,
            "bancos_adicionais": None,
            "servicos_monitorados": json.dumps({
                "systemd": ["sistemalec", "nginx"],
                "extra_http": [{"nome": "FastAPI Docs", "url": "http://10.34.0.202:8000/docs"}],
            }),
        },
        {
            "nome": "Metabase",
            "descricao": "Ferramenta corporativa de Business Intelligence",
            "url_base": "http://10.34.0.114:3000",
            "possui_rota_health": True,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": True,
            "zabbix_host_id": "HC-UFPE-VP-METABASE",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "metabase",
            "http_headers": json.dumps({"Host": "relatorios.hc-ufpe.ebserh"}),
            "bancos_adicionais": json.dumps([
                {"nome": "PostgreSQL Metabase", "host": "10.34.0.114", "porta": 5432},
            ]),
            "servicos_monitorados": json.dumps({
                "systemd": ["metabase", "nginx", "postgresql@15-main"],
            }),
        },
        {
            "nome": "CSH (Maqueiros) - Produção",
            "descricao": "Gestão de serviços de hotelaria e maqueiros",
            "url_base": "http://10.34.0.111/admin_3/loginAD.php",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": "HCPE-VP-MAQUEIROS",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "maqueiros",
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "MariaDB CSH", "host": "10.34.0.111", "porta": 3306},
            ]),
            "servicos_monitorados": json.dumps({
                "systemd": ["apache2", "mariadb"],
            }),
        },
        {
            "nome": "Dialsist",
            "descricao": "Sistema de gestão de diálise",
            "url_base": "http://10.34.0.83/ufpeds4/",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": "HC-UFPE-VP-DIALSIST",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "dialsist",
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "MySQL Dialsist", "host": "10.34.0.83", "porta": 3306},
                {"nome": "AGHU Slave", "host": "10.34.0.92", "porta": 5432},
            ]),
            "servicos_monitorados": json.dumps({
                "systemd": ["apache2", "mysql"],
            }),
        },
        {
            "nome": "GED Linus",
            "descricao": "Gestão eletrônica de documentos (e-Custódia)",
            "url_base": "http://10.34.0.124/usuarios/sign_in",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": False,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": "HC-UFPE-VP-GED",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "ged",
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "NFSv4 GED", "host": "10.34.0.124", "porta": 2049},
            ]),
            "servicos_monitorados": json.dumps({
                "systemd": ["nginx"],
                "processes": ["puma"],
            }),
        },
        {
            "nome": "Integração AGHU x Master Tools",
            "descricao": "Robô Java Tomcat de sincronização AGHU x Master Tools",
            "url_base": "http://10.34.0.4:8080/",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": "HCPE-VP-TOMCAT",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "integracao-master",
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "Oracle Master VIP", "host": "10.34.1.125", "porta": 1521},
            ]),
            "servicos_monitorados": json.dumps({
                "systemd": ["tomcat"],
                "tomcat_app": "IntegracaoMasterAghu",
            }),
        },
        {
            "nome": "Master Tools - Node 1 (RAC01)",
            "descricao": "Cluster Oracle RAC e Forms/Reports - Nó 1 (rac01)",
            "url_base": "http://10.34.1.120/",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": "HCPE-FP-MASTER01",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "master01",
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "Oracle RAC01", "host": "10.34.1.120", "porta": 1521},
                {"nome": "Oracle VIP .122", "host": "10.34.1.122", "porta": 1521},
                {"nome": "Oracle VIP .125", "host": "10.34.1.125", "porta": 1521},
                {"nome": "Oracle VIP .126", "host": "10.34.1.126", "porta": 1521},
            ]),
            "servicos_monitorados": json.dumps({
                "systemd": ["oracle-ohasd"],
                "processes": ["ora_pmon_hcpe1", "tnslsnr"],
                "extra_http": [{"nome": "Node Exporter", "url": "http://10.34.1.120:9100/metrics"}],
            }),
        },
        {
            "nome": "Master Tools - Node 2 (RAC02)",
            "descricao": "Cluster Oracle RAC e Forms/Reports - Nó 2 (rac02)",
            "url_base": "http://10.34.1.121/",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": "HCPE-FP-MASTER02",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": "master02",
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "Oracle RAC02", "host": "10.34.1.121", "porta": 1521},
                {"nome": "Oracle VIP .123", "host": "10.34.1.123", "porta": 1521},
                {"nome": "Oracle VIP .124", "host": "10.34.1.124", "porta": 1521},
            ]),
            "servicos_monitorados": json.dumps({
                "systemd": ["oracle-ohasd"],
                "processes": ["ora_pmon_hcpe2", "tnslsnr"],
            }),
        },
        {
            "nome": "RealBlood",
            "descricao": "Gestão de agência transfusional (IIS APP + SQL Server BD)",
            "url_base": "http://10.34.0.218/",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": "HC-UFPE-VP-REALBLOOD-APP",
            "criticidade": "ALTA",
            "tipo_checagem": "HTTP",
            "porta_tcp": None,
            "ssh_host": None,
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "SQL Server RealBlood", "host": "10.34.0.217", "porta": 1433},
                {"nome": "IIS RealBlood BD", "host": "10.34.0.217", "porta": 80},
            ]),
            "servicos_monitorados": None,
        },
        {
            "nome": "Gateway Power BI",
            "descricao": "On-premises Data Gateway Windows (sem servidor HTTP)",
            "url_base": "10.34.0.70",
            "possui_rota_health": False,
            "url_health": "/api/health",
            "possui_banco_aghu": True,
            "monitora_usuarios_ativos": False,
            "zabbix_host_id": "HC-UFPE-VP-ONPREMISSES",
            "criticidade": "MEDIA",
            "tipo_checagem": "TCP",
            "porta_tcp": 10050,
            "ssh_host": None,
            "http_headers": None,
            "bancos_adicionais": json.dumps([
                {"nome": "RDP Gateway BI", "host": "10.34.0.70", "porta": 3389},
            ]),
            "servicos_monitorados": None,
        },
    ]


async def seed_monitored_systems(session: AsyncSession) -> int:
    """Insere os sistemas mapeados caso ainda não existam em data/app.db."""
    inserted = 0
    for item in get_seed_applications_data():
        res = await session.execute(select(Aplicacao).where(Aplicacao.nome == item["nome"]))
        existing = res.scalar_one_or_none()
        if existing is None:
            session.add(Aplicacao(**item, ativo=True))
            inserted += 1
        else:
            for field in ("tipo_checagem", "porta_tcp", "ssh_host", "http_headers", "servicos_monitorados"):
                if getattr(existing, field, None) is None and item.get(field) is not None:
                    setattr(existing, field, item[field])
    await session.commit()
    return inserted
