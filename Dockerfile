FROM alpine:3.10 AS config-builder
WORKDIR /usr/src/app

RUN apk add --update --no-cache python3 ca-certificates && python3 -m pip install --upgrade pip

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY config/* ./
RUN python3 isc_dhcp_config_gen.py > kea-dhcp4.conf

FROM alpine:3.10 as builder

ARG KEA_DHCP_VERSION=1.6.0
ARG LOG4_CPLUS_VERSION=1.2.2

RUN apk add --no-cache --virtual .build-deps \
        alpine-sdk \
        bash \
        boost-dev \
        bzip2-dev \
        file \
        libressl-dev \
        zlib-dev \
        tar \
        gzip && \
    curl -sL https://sourceforge.net/projects/log4cplus/files/log4cplus-stable/${LOG4_CPLUS_VERSION}/log4cplus-${LOG4_CPLUS_VERSION}.tar.gz | tar -zx -C /tmp && \
    cd /tmp/log4cplus-${LOG4_CPLUS_VERSION} && \
    ./configure && \
    make -s -j$(nproc) && \
    make install && \
    curl -sL https://ftp.isc.org/isc/kea/${KEA_DHCP_VERSION}/kea-${KEA_DHCP_VERSION}.tar.gz | tar -zx -C /tmp && \
    cd /tmp/kea-${KEA_DHCP_VERSION} && \
    ./configure \
        --enable-shell && \
    make -s -j$(nproc) && \
    make install-strip && \
    apk del --purge .build-deps && \
    rm -rf /tmp/*

FROM alpine:3.10 AS runtime
LABEL maintainer="NPFLAN-SERVERTEAM"

RUN apk --no-cache add \
        boost \
        bzip2 \
        libressl \
        zlib

COPY --from=builder /usr/local /usr/local/
COPY --from=config-builder /usr/src/app/kea-*conf /etc/kea/

EXPOSE 67/udp 67/tcp 68/udp 68/tcp

ENTRYPOINT ["/usr/local/sbin/kea-dhcp4"]
CMD ["-c", "/etc/kea/kea-dhcp4.conf"]