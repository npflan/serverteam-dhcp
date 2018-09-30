FROM alpine:3.6 AS builder
WORKDIR /usr/src/app

RUN apk add --no-cache python3 ca-certificates

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY config/isc_dhcp_config_gen.py .
RUN python3 isc_dhcp_config_gen.py > dhcpd.conf

FROM alpine:3.6 AS runtime
WORKDIR /usr/src/app
RUN apk add --no-cache dhcp ca-certificates

RUN mkdir -p /dhcp/config/ \
    && touch /var/lib/dhcp/dhcpd.leases

COPY --from=builder /usr/src/app/dhcpd.conf /dhcp/config/dhcpd.conf
COPY config/reservation.ip.*.conf /dhcp/config/
EXPOSE 67/udp

ENTRYPOINT [ "/usr/sbin/dhcpd", "-d", "-f", "-cf", "/dhcp/config/dhcpd.conf" ]