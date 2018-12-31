{% set puser = salt['pillar.get']('puser',) %}
{% set dpath = salt['pillar.get']('dpath',) %}
{% set dname = salt['pillar.get']('dname',) %}
{% set dtime = salt['pillar.get']('dtime',) %}

backup_dir:
  file.directory:
    - name: /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}
    - user: {{ puser }}
    - group: {{ puser }}
    - makedirs: True
    - recurse:
      - user
      - group

  cmd.run:
    - name: /bin/cp -rf /home/{{ puser }}/{{ dpath }}/webapps/{{ dname }}* /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }} || (rm -rf /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }} && exit 2)
    - user: {{ puser }}
    - group: {{ puser }}
    - unless: test ! -d /home/{{ puser }}/backup/full/{{ dpath }}/{{ dtime }}

