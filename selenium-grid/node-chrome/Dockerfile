FROM selenium/node-chrome:latest

ENV SE_EVENT_BUS_HOST=selenium-hub
ENV SE_EVENT_BUS_PUBLISH_PORT=4442
ENV SE_EVENT_BUS_SUBSCRIBE_PORT=4443

EXPOSE 5555

CMD ["selenium-server", "standalone"]
