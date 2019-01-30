# Open nvidia-docker2 GL support
COPY --from=glvnd /usr/local/lib/x86_64-linux-gnu /usr/local/lib/x86_64-linux-gnu
COPY --from=glvnd /usr/local/lib/i386-linux-gnu /usr/local/lib/i386-linux-gnu
COPY --from=glvnd /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu
COPY --from=glvnd /usr/lib/i386-linux-gnu /usr/lib/i386-linux-gnu

COPY --from=glvnd /usr/local/share/glvnd/egl_vendor.d/10_nvidia.json /usr/local/share/glvnd/egl_vendor.d/10_nvidia.json

# if the path is alreaady present don't fail because of being unable to append
RUN ( echo '/usr/local/lib/x86_64-linux-gnu' >> /etc/ld.so.conf.d/glvnd.conf && ldconfig || grep -q /usr/local/lib/x86_64-linux-gnu /etc/ld.so.conf.d/glvnd.conf ) && \
    ( echo '/usr/local/lib/i386-linux-gnu' >> /etc/ld.so.conf.d/glvnd.conf &&  ldconfig || grep -q /usr/local/lib/i386-linux-gnu /etc/ld.so.conf.d/glvnd.conf )

ENV LD_LIBRARY_PATH /usr/local/lib/x86_64-linux-gnu:/usr/local/lib/i386-linux-gnu${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

ENV NVIDIA_VISIBLE_DEVICES ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics