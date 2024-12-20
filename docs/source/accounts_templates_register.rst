=====================
Plantilla de Registro
=====================

Esta es la plantilla HTML para la página de registro.

Extiende de la plantilla base ``layout.html`` y muestra mensajes incluidos desde ``includes/messages.html``.

Título de la página
===================
.. code-block:: html+django

    {% block title %}Registrarse{% endblock %}

Cuerpo de la página
===================
.. code-block:: html+django

    {% block body %}
    <div class="container mt-5 mb-5">
      {% load static %}
    <form method="post" action="{% url 'accounts:register' %}">
      {% csrf_token %}
      <h1 class="text-center">
        Registrarse
      </h1>
      <div class="mb-3">
        <label for="username" class="form-label">
          Nombre de usuario
        </label>
        <input type="text" class="form-control" id="username" name="username" placeholder="Nombre de usuario" aria-describedby="usernameHelp" required autofocus>
        <ul class="usernameHelp">
          <li class="form-text">Debe ser único.</li>
        </ul>
      </div>
      <div class="row mb-3">
        <div class="col-xs-12 col-sm-6">
          <label for="firstname" class="form-label">
            Nombre
          </label>
          <input type="text" id="firstname" class="form-control" placeholder="Nombre" name="firstname" required>
        </div>
        <div class="col-xs-12 col-sm-6">
          <label for="lastname" class="form-label">
            Apellido
          </label>
          <input type="text" id="lastname" class="form-control" placeholder="Apellido (opcional)" name="lastname">
        </div>
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">
          Correo electrónico
        </label>
        <input type="email" class="form-control" id="email" name="email" placeholder="Correo electrónico" required>
      </div>
      <div class="mb-3">
        <label for="password1" class="form-label">
          Contraseña
        </label>
        <input type="password" class="form-control" id="password1" name="password1" placeholder="Contraseña" aria-describedby="passwordHelp" required>
        <ul class="passwordHelp">
          <li class="form-text">La longitud mínima debe ser 6 caracteres.</li>
          <li class="form-text">Se requiere un dígito.</li>
          <li class="form-text">Se requiere un caracter especial.</li>
        </ul>
      </div>
      <div class="mb-3">
        <label for="password2" class="form-label">
          Confirmar contraseña
        </label>
        <input type="password" class="form-control" id="password2" name="password2" placeholder="Confirmar contraseña" required>
      </div>
      <div class="form-check mb-3">
        <input class="form-check-input" type="checkbox" value="" id="agreeCheckbox" required>
        <label class="form-check-label" for="invalidCheck">
          Acepto los <a class="text-decoration-none" data-bs-toggle="modal" data-bs-target="#termsModal">
            términos y condiciones
          </a> 
        </label>
      </div>
      <button type="submit" class="btn btn-success w-100">Registrarse</button>
      <div class="mt-3">
        <p>Ya tienes cuenta? <a href="{% url 'accounts:login' %}" class="text-decoration-none">Iniciar sesión</a></p>
      </div>
    </form>
    </div>
    <div class="modal fade" id="termsModal" tabindex="-1" aria-labelledby="termsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="termsModalLabel">Términos y condiciones</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>
              Al registrarse, usted acepta cumplir con los términos y condiciones de nuestro sitio web. Esto incluye, entre otras cosas, respetar la privacidad de otros usuarios, abstenerse de publicar contenido inapropiado y cumplir con todas las leyes y regulaciones aplicables.
              <a href="{% url 'terms_and_conditions' %}" class="text-decoration-none">Leer más</a>
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            <button type="button" class="btn btn-primary" onclick="handleAgree()">Aceptar</button>
          </div>
        </div>
      </div>
    </div>
    <script src="{% static 'js/accounts/register.js' %}"></script>
    {% endblock %}