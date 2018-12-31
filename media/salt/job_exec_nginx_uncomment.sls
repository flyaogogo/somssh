{% set slang = salt['grains.get']('locale_info:defaultlanguage',) %}
{% set sencode = salt['grains.get']('locale_info:defaultencoding',) %}
{% set dest_file = salt['pillar.get']('dest_file',) %}
{% set backends = salt['pillar.get']('backends',) %}
{% set port = salt['pillar.get']('port',) %}

{% for bk in backends %}
upsteam-{{ bk }}-{{ port }}:
  file.replace:
    - name: {{ dest_file }}
    - pattern: '^\t####server {{ bk }}:{{ port }}'
    - repl: '\tserver {{ bk }}:{{ port }}'
    - backup: False
{% endfor %}

nginx-reload:
  cmd.run:
    - name: sudo /opt/nginx/sbin/nginx -t && sudo /opt/nginx/sbin/nginx -s reload
    - env:
      - LC_ALL: "{{ slang }}.{{ sencode }}"
    #- watch:
    - onchanges:
      - file: {{ dest_file }}
