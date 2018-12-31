{% set spath = salt['pillar.get']('spath',) %}
{% set dpath = salt['pillar.get']('dpath',) %}

file_upload:
  file.recurse:
    - name: {{ dpath }}
    - dir_mode: 2755
    - source: salt://file.manage/upload/{{ spath }}
    - include_empty: True
    - backup: minion
