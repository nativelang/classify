# Prepare the Java release bundle

From the Classify checkout, use Python 3.10+, GnuPG, and Eclipse Temurin 21.0.13.1 on `PATH` to build the v0.3.0 JAR. Supply the Gson 2.15.0 JAR and the full fingerprint of the release signing key.

```sh
python3 bindings/java/central-bundle.py gson-2.15.0.jar "$SIGNING_FINGERPRINT" classify-central.zip
```

The command checks the binary against its pinned digest, then packages it with its POM, sources, Javadoc, detached signatures and checksums. Review the bundle and make the signing public key available to Central before uploading. [Sonatype signing requirements](https://central.sonatype.org/publish/requirements/gpg/) · [Central Portal bundle upload](https://central.sonatype.org/publish/publish-portal-upload/)
