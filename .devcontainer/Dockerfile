FROM python:3.13-alpine
ARG USERNAME=dev
ARG USER_UID=1001
ARG USER_GID=$USER_UID

# Install needed packages
RUN apk update && apk upgrade
RUN apk add bash git fish curl sudo nodejs npm

# Create a new non-root user
RUN apk add shadow
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# install firefox and some fonts
RUN apk add font-terminus font-inconsolata font-dejavu font-noto font-noto-cjk font-awesome font-noto-extra
RUN apk add firefox

# let dev sudo without password
RUN echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USERNAME
