#!/bin/bash

# Iniciar una nueva sesión de tmux
tmux new-session -d -s mysession

# Iniciar el servidor de Django en la primera ventana
tmux send-keys -t mysession "python manage.py runserver" C-m

# Crear una nueva ventana y ejecutar el worker de Celery
tmux new-window -t mysession
tmux send-keys -t mysession:1 "celery -A cloudcms worker --loglevel=info" C-m

# Crear otra ventana y ejecutar el beat scheduler de Celery
tmux new-window -t mysession
tmux send-keys -t mysession:2 "celery -A cloudcms beat --loglevel=info" C-m

# Adjuntar a la sesión de tmux
tmux attach-session -t mysession