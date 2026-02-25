#!/usr/bin/env python3
"""
PKI Setup Script for Timestamping Server
Generates: Root CA -> Intermediate CA -> Server Cert -> Client Cert (.p12)
"""

import datetime
import ipaddress
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12

PKI_DIR = Path("pki")

CONFIG = {
    "country":          "MK",
    "state":            "Skopje",
    "org":              "FINKI Timestamping Server",
    "root_cn":          "FINKI Root CA",
    "intermediate_cn":  "FINKI Intermediate CA",
    "server_cn":        "localhost",
    "client_cn":        "timestamping-client",
    "p12_password":     b"changeit",
    "root_days":        3650,
    "intermediate_days": 1825,
    "leaf_days":        375,
}

def generate_key(size=2048):
    return rsa.generate_private_key(public_exponent=65537, key_size=size)

def save_key(key, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    print(f"  [+] Key saved:  {path}")

def save_cert(cert, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print(f"  [+] Cert saved: {path}")

def make_name(cn: str) -> x509.Name:
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, CONFIG["country"]),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, CONFIG["state"]),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, CONFIG["org"]),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
    ])

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

def days(n):
    return utcnow() + datetime.timedelta(days=n)

def create_root_ca():
    print("\n--- Generating Root CA ---")
    key = generate_key(4096)
    name = make_name(CONFIG["root_cn"])
    
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(utcnow()).not_valid_after(days(CONFIG["root_days"]))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(x509.KeyUsage(True, True, True, False, False, False, False, False, False), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .sign(key, hashes.SHA256())
    )
    save_key(key, PKI_DIR / "root-ca" / "private" / "ca.key.pem")
    save_cert(cert, PKI_DIR / "root-ca" / "certs" / "ca.cert.pem")
    return key, cert

def create_intermediate_ca(root_key, root_cert):
    print("\n--- Generating Intermediate CA ---")
    key = generate_key(4096)
    name = make_name(CONFIG["intermediate_cn"])
    
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(root_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(utcnow()).not_valid_after(days(CONFIG["intermediate_days"]))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.KeyUsage(True, True, True, False, False, False, False, False, False), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()), critical=False)
        .sign(root_key, hashes.SHA256())
    )
    save_key(key, PKI_DIR / "intermediate-ca" / "private" / "intermediate.key.pem")
    save_cert(cert, PKI_DIR / "intermediate-ca" / "certs" / "intermediate.cert.pem")
    
    chain = PKI_DIR / "intermediate-ca" / "certs" / "ca-chain.cert.pem"
    chain.write_bytes(cert.public_bytes(serialization.Encoding.PEM) + root_cert.public_bytes(serialization.Encoding.PEM))
    print(f"  [+] CA Chain saved: {chain}")
    return key, cert

def create_server_cert(int_key, int_cert):
    print("\n--- Generating Server Certificate ---")
    key = generate_key(2048)
    name = make_name(CONFIG["server_cn"])
    
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(int_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(utcnow()).not_valid_after(days(CONFIG["leaf_days"]))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(True, False, False, False, False, True, False, False, False), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("timestamping.local"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]), critical=False)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(int_key.public_key()), critical=False)
        .sign(int_key, hashes.SHA256())
    )
    save_key(key, PKI_DIR / "server" / "server.key.pem")
    save_cert(cert, PKI_DIR / "server" / "server.cert.pem")
    
    fullchain = PKI_DIR / "server" / "server.fullchain.pem"
    fullchain.write_bytes(cert.public_bytes(serialization.Encoding.PEM) + int_cert.public_bytes(serialization.Encoding.PEM))
    print(f"  [+] Fullchain saved: {fullchain}")

def create_client_cert(int_key, int_cert):
    print("\n--- Generating Client Certificate ---")
    key = generate_key(2048)
    name = make_name(CONFIG["client_cn"])
    
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(int_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(utcnow()).not_valid_after(days(CONFIG["leaf_days"]))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(True, True, False, False, False, True, False, False, False), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(int_key.public_key()), critical=False)
        .sign(int_key, hashes.SHA256())
    )
    save_key(key, PKI_DIR / "client" / "client.key.pem")
    save_cert(cert, PKI_DIR / "client" / "client.cert.pem")
    
    p12_data = pkcs12.serialize_key_and_certificates(
        name=b"Timestamping Client",
        key=key, cert=cert, cas=[int_cert],
        encryption_algorithm=serialization.BestAvailableEncryption(CONFIG["p12_password"])
    )
    p12_path = PKI_DIR / "client" / "client.p12"
    p12_path.write_bytes(p12_data)
    print(f"  [+] Client P12 saved: {p12_path} (Password: changeit)")

if __name__ == "__main__":
    if (PKI_DIR / "server" / "server.key.pem").exists():
        if input("PKI exists. Overwrite? (y/N): ").strip().lower() != 'y':
            exit("Aborted.")
            
    root_key, root_cert = create_root_ca()
    int_key, int_cert = create_intermediate_ca(root_key, root_cert)
    create_server_cert(int_key, int_cert)
    create_client_cert(int_key, int_cert)
    print("\n PKI generation complete!")
