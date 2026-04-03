FROM texlive/texlive:latest

ARG USERNAME=texlive

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends openssh-client graphviz \
  && rm -rf /var/lib/apt/lists/* \
  && mkdir -p /home/${USERNAME}/.ssh \
  && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh \
  && chmod 700 /home/${USERNAME}/.ssh

USER $USERNAME

WORKDIR /workspace