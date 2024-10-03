
CREATE TABLE public.Etiquetas (
                id_etiqueta VARCHAR NOT NULL,
                CONSTRAINT etiquetas_pk PRIMARY KEY (id_etiqueta)
);


CREATE SEQUENCE public.estado_seq_1;

CREATE TABLE public.Estado (
                id_estado SMALLINT NOT NULL DEFAULT nextval('public.estado_seq_1'),
                nombre VARCHAR NOT NULL,
                anterior_estado INTEGER DEFAULT 0 NOT NULL,
                motivo VARCHAR,
                CONSTRAINT estado_pk PRIMARY KEY (id_estado)
);


ALTER SEQUENCE public.estado_seq_1 OWNED BY public.Estado.id_estado;

CREATE SEQUENCE public.rol_seq;

CREATE TABLE public.Roles (
                id_rol SMALLINT NOT NULL DEFAULT nextval('public.rol_seq'),
                nombre VARCHAR NOT NULL,
                CONSTRAINT roles_pk PRIMARY KEY (id_rol)
);


ALTER SEQUENCE public.rol_seq OWNED BY public.Roles.id_rol;

CREATE SEQUENCE public.categoria_seq_1;

CREATE TABLE public.Categorias (
                id_categoria SMALLINT NOT NULL DEFAULT nextval('public.categoria_seq_1'),
                moderada BOOLEAN NOT NULL,
                nombre VARCHAR NOT NULL,
                visibilidad SMALLINT NOT NULL,
                descripcion VARCHAR NOT NULL,
                CONSTRAINT categorias_pk PRIMARY KEY (id_categoria)
);


ALTER SEQUENCE public.categoria_seq_1 OWNED BY public.Categorias.id_categoria;

CREATE SEQUENCE public.usuario_seq;

CREATE TABLE public.Usuarios (
                id_usuario INTEGER NOT NULL DEFAULT nextval('public.usuario_seq'),
                nombre VARCHAR NOT NULL,
                avatar VARCHAR,
                fecha_registro DATE NOT NULL,
                fecha_nacimiento DATE,
                password VARCHAR NOT NULL,
                correo VARCHAR NOT NULL,
                contacto VARCHAR,
                CONSTRAINT usuarios_pk PRIMARY KEY (id_usuario)
);


ALTER SEQUENCE public.usuario_seq OWNED BY public.Usuarios.id_usuario;

CREATE SEQUENCE public.favoritos_id_favorito_seq;

CREATE TABLE public.Favoritos (
                id_favorito INTEGER NOT NULL DEFAULT nextval('public.favoritos_id_favorito_seq'),
                id_usuario INTEGER NOT NULL,
                id_categoria SMALLINT NOT NULL,
                CONSTRAINT favoritos_pk PRIMARY KEY (id_favorito)
);


ALTER SEQUENCE public.favoritos_id_favorito_seq OWNED BY public.Favoritos.id_favorito;

CREATE SEQUENCE public.suscripcion_seq;

CREATE TABLE public.Suscripciones (
                id_suscripcion INTEGER NOT NULL DEFAULT nextval('public.suscripcion_seq'),
                id_categoria SMALLINT NOT NULL,
                id_usuario INTEGER NOT NULL,
                fecha_suscripcion TIMESTAMP NOT NULL,
                CONSTRAINT suscripciones_pk PRIMARY KEY (id_suscripcion)
);


ALTER SEQUENCE public.suscripcion_seq OWNED BY public.Suscripciones.id_suscripcion;

CREATE SEQUENCE public.publicacion_seq;

CREATE TABLE public.Publicaciones (
                id_publicacion INTEGER NOT NULL DEFAULT nextval('public.publicacion_seq'),
                titulo VARCHAR NOT NULL,
                resumen VARCHAR,
                contenido VARCHAR,
                thumbnail VARCHAR,
                id_usuario INTEGER NOT NULL,
                fecha_creado TIMESTAMP NOT NULL,
                vigencia DATE,
                id_categoria SMALLINT NOT NULL,
                calificacion INTEGER DEFAULT 0 NOT NULL,
                destacado BOOLEAN NOT NULL,
                id_estado SMALLINT NOT NULL,
                CONSTRAINT publicaciones_pk PRIMARY KEY (id_publicacion)
);


ALTER SEQUENCE public.publicacion_seq OWNED BY public.Publicaciones.id_publicacion;

CREATE TABLE public.Publicacion_Etiqueta (
                id_etiqueta VARCHAR NOT NULL,
                id_publicacion INTEGER NOT NULL,
                CONSTRAINT publicacion_etiqueta_pk PRIMARY KEY (id_etiqueta, id_publicacion)
);


CREATE SEQUENCE public.comentario_seq;

CREATE TABLE public.Comentarios (
                id_comentario INTEGER NOT NULL DEFAULT nextval('public.comentario_seq'),
                comentario VARCHAR NOT NULL,
                id_usuario INTEGER NOT NULL,
                id_publicacion INTEGER NOT NULL,
                fecha_comentado TIMESTAMP NOT NULL,
                CONSTRAINT comentarios_pk PRIMARY KEY (id_comentario)
);


ALTER SEQUENCE public.comentario_seq OWNED BY public.Comentarios.id_comentario;

CREATE SEQUENCE public.likes_seq;

CREATE TABLE public.Likes (
                id_like INTEGER NOT NULL DEFAULT nextval('public.likes_seq'),
                id_usuario INTEGER NOT NULL,
                id_publicacion INTEGER NOT NULL,
                CONSTRAINT likes_pk PRIMARY KEY (id_like)
);


ALTER SEQUENCE public.likes_seq OWNED BY public.Likes.id_like;

CREATE SEQUENCE public.compartidos_seq;

CREATE TABLE public.Compartidos (
                id_compartido INTEGER NOT NULL DEFAULT nextval('public.compartidos_seq'),
                id_usuario INTEGER NOT NULL,
                id_publicacion INTEGER NOT NULL,
                CONSTRAINT compartidos_pk PRIMARY KEY (id_compartido)
);


ALTER SEQUENCE public.compartidos_seq OWNED BY public.Compartidos.id_compartido;

CREATE SEQUENCE public.reporte_seq;

CREATE TABLE public.Reportes (
                id_reporte INTEGER NOT NULL DEFAULT nextval('public.reporte_seq'),
                id_usuario INTEGER NOT NULL,
                motivo VARCHAR NOT NULL,
                fecha_generado TIMESTAMP NOT NULL,
                fecha_atendido TIMESTAMP,
                id_publicacion INTEGER NOT NULL,
                CONSTRAINT reportes_pk PRIMARY KEY (id_reporte)
);


ALTER SEQUENCE public.reporte_seq OWNED BY public.Reportes.id_reporte;

CREATE TABLE public.Usuarios_Roles (
                id_usuario INTEGER NOT NULL,
                id_rol SMALLINT NOT NULL,
                CONSTRAINT usuarios_roles_pk PRIMARY KEY (id_usuario, id_rol)
);


ALTER TABLE public.Publicacion_Etiqueta ADD CONSTRAINT etiquetas_publicacion_etiqueta_fk
FOREIGN KEY (id_etiqueta)
REFERENCES public.Etiquetas (id_etiqueta)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Publicaciones ADD CONSTRAINT estado_publicaciones_fk
FOREIGN KEY (id_estado)
REFERENCES public.Estado (id_estado)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Usuarios_Roles ADD CONSTRAINT roles_usuarios_roles_fk
FOREIGN KEY (id_rol)
REFERENCES public.Roles (id_rol)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Publicaciones ADD CONSTRAINT categorias_publicaciones_fk
FOREIGN KEY (id_categoria)
REFERENCES public.Categorias (id_categoria)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Suscripciones ADD CONSTRAINT categorias_suscripciones_fk
FOREIGN KEY (id_categoria)
REFERENCES public.Categorias (id_categoria)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Favoritos ADD CONSTRAINT categorias_favoritos_fk
FOREIGN KEY (id_categoria)
REFERENCES public.Categorias (id_categoria)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Usuarios_Roles ADD CONSTRAINT usuarios_usuarios_roles_fk
FOREIGN KEY (id_usuario)
REFERENCES public.Usuarios (id_usuario)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Publicaciones ADD CONSTRAINT usuarios_publicaciones_fk
FOREIGN KEY (id_usuario)
REFERENCES public.Usuarios (id_usuario)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Reportes ADD CONSTRAINT usuarios_reportes_fk
FOREIGN KEY (id_usuario)
REFERENCES public.Usuarios (id_usuario)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Compartidos ADD CONSTRAINT usuarios_compartidos_fk
FOREIGN KEY (id_usuario)
REFERENCES public.Usuarios (id_usuario)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Likes ADD CONSTRAINT usuarios_likes_fk
FOREIGN KEY (id_usuario)
REFERENCES public.Usuarios (id_usuario)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Comentarios ADD CONSTRAINT usuarios_comentarios_fk
FOREIGN KEY (id_usuario)
REFERENCES public.Usuarios (id_usuario)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Suscripciones ADD CONSTRAINT usuarios_suscripciones_fk
FOREIGN KEY (id_usuario)
REFERENCES public.Usuarios (id_usuario)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Favoritos ADD CONSTRAINT usuarios_favoritos_fk
FOREIGN KEY (id_usuario)
REFERENCES public.Usuarios (id_usuario)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Reportes ADD CONSTRAINT publicaciones_reportes_fk
FOREIGN KEY (id_publicacion)
REFERENCES public.Publicaciones (id_publicacion)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Compartidos ADD CONSTRAINT publicaciones_compartidos_fk
FOREIGN KEY (id_publicacion)
REFERENCES public.Publicaciones (id_publicacion)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Likes ADD CONSTRAINT publicaciones_likes_fk
FOREIGN KEY (id_publicacion)
REFERENCES public.Publicaciones (id_publicacion)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Comentarios ADD CONSTRAINT publicaciones_comentarios_fk
FOREIGN KEY (id_publicacion)
REFERENCES public.Publicaciones (id_publicacion)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.Publicacion_Etiqueta ADD CONSTRAINT publicaciones_publicacion_etiqueta_fk
FOREIGN KEY (id_publicacion)
REFERENCES public.Publicaciones (id_publicacion)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;