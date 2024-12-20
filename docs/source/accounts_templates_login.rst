====================
Plantilla de Login
====================

Esta es la plantilla HTML para la página de inicio de sesión.

Extiende de la plantilla base ``layout.html`` y muestra mensajes incluidos desde ``includes/messages.html``.

Título de la página
===================
.. code-block:: html+django

    {% block title %}Inicia sesión{% endblock %}

Cuerpo de la página
===================
.. code-block:: html+django

    {% block body %}
    <div class="container mt-5 mb-5">
    <form method="post" action="{% url 'accounts:login' %}">
      {% csrf_token %}
      <h1 class="text-center">
        Iniciar
      </h1>
      <div class="mb-3">
        <label for="username" class="form-label">
          Nombre de usuario
        </label>
        <input type="text" class="form-control" id="username" aria-describedby="usernameHelp" name="username" placeholder="Nombre de usuario" required autofocus>
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">
          Contraseña
        </label>
        <input type="password" class="form-control" id="password" name="password" placeholder="Contraseña" required>
      </div>
      <div>
        <a href="#" class="float-end text-decoration-none">Olvidaste tu contraseña?</a>
      </div>
      <button type="submit" class="btn btn-success w-100 mt-3">Iniciar sesión</button>
      <div class="mt-3">
        <p>No tienes cuenta? <a href="{% url 'accounts:register' %}" class="text-decoration-none">Registrarse</a></p>
      </div>
    </form>
    </div>
    {% endblock %}