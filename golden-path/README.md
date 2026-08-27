# Fase 2: Construcción del Golden Path

El objetivo es investigar la anatomía de los Software Templates de Backstage y construir tu propio Golden Path para crear microservicios NodeJS de forma automatizada.

## ¿Qué es un Golden Path?

En el contexto de Plataforma de Ingeniería, un **Golden Path** es la ruta pre-aprobada que la plataforma ofrece a los equipos de desarrollo para realizar una tarea de forma segura, eficiente y consistente.

Un desarrollador no necesita saber cómo configurar un repositorio, un pipeline de CI/CD, o un manifiesto de Kubernetes: simplemente llena un formulario y obtiene un servicio listo para producción.

En Backstage, los Golden Paths se implementan mediante **Software Templates**, definidas en archivos `template.yaml`.

---

## Investigación

Antes de escribir código, debes investigar la documentación oficial de Backstage. Esta sección contiene **preguntas guía** que debes responder como parte de esta actividad.

### Recursos clave para investigar

| Recurso | URL |
|---|---|
| Documentación de Software Templates | https://backstage.io/docs/features/software-templates/ |
| Referencia de `template.yaml` (fields) | https://backstage.io/docs/features/software-templates/writing-templates |
| Built-in Actions del Scaffolder | https://backstage.io/docs/features/software-templates/builtin-actions |
| Referencia de Nunjucks (motor de plantillas) | https://mozilla.github.io/nunjucks/templating.html |
| Publicar en GitHub con Backstage | https://backstage.io/docs/features/software-templates/builtin-actions#publish-github |

### 1. Anatomía de un `template.yaml`

Un `template.yaml` es un archivo YAML que Backstage interpreta para renderizar un formulario y orquestar acciones.

#### 1.1 Estructura general

Investiga y responde: ¿Cuáles son las **4 secciones principales** de un `template.yaml`? Describe brevemente el propósito de cada una.

El template.yaml es una de las entidades de catalogo en Backstage, por lo que se respeta un formato estandar de entidades, el cual es el siguiente: 

| Sección | Propósito |
|---|---|
| `apiVersion` | Versión del esquema que interpreta el Scaffolder. Para templates actuales: `scaffolder.backstage.io/v1beta3`. Define qué sintaxis de plantillas se usa (`${{ }}` con Nunjucks) y qué campos son válidos. |
| `kind` | Es el tipo de entidad. Siempre `Template`. Es lo que hace que Backstage la muestre en la sección **Create** en lugar de tratarla como un componente más. |
| `metadata` | Identidad y presentación del template: `name`, `title` y `description` (lo que ve el desarrollador en la tarjeta), `tags` (filtros de búsqueda) y `annotations`. |
| `spec` | El comportamiento del template: `owner` (equipo dueño), `type` (service, website, library…) y los tres bloques funcionales: `parameters` (formulario), `steps` (orquestación) y `output` (resultado mostrado al usuario). |

> Nota: Parameters, steps y output no son secciones de primer nivel, estan dentro de SPEC. Suele pasar que se puedan escribir al mismo nivel que metadata. 

#### 1.2 Metadata del Template

Investiga los campos del bloque `metadata`. ¿Qué es el campo `annotations` y para qué sirve en el contexto de los templates?

El bloque de 'Metadata' acepta los campos comunes de cualquier entidad, los cuales corresponde a: 

| Campo | Uso |
|---|---|
| `name` | Identificador único dentro del namespace. Es el que aparece en el `entityRef` (`template:default/nodejs-microservice`). |
| `title` | Nombre legible visible en la interfaz de usuario. |
| `description` | Texto de la tarjeta en el portal. |
| `tags` | Etiquetas de filtrado. La etiqueta `recommended` es una convención para señalar cuál es el camino "dorado" cuando hay varios templates similares. |
| `annotations` | Pares clave/valor que **conectan la entidad con sistemas externos**. |

Por ultimo los `annotations` son metadatos que no logran cambiar el comportamient del catalogo por si mismos, solo que actuan como enganches para plugins o integraciones, buscando que cada plugin busque la anotacion que corresponda. y si llegase a encontrarla habilita su funcionalidad para esa entidad.

### 2. Parámetros de Entrada (`parameters`)

La sección `parameters` define el formulario que verá el desarrollador. Es el contrato de tu API de Plataforma.

#### 2.1 Tipos de campos (`ui:widget`)

Backstage usa JSON Schema para definir los campos del formulario. Investiga y lista al menos **5 tipos de campos** disponibles y cuándo usarías cada uno.

Consultando, se podrian tener ui:widget y ui:field, el widget es nativo funcionando como schemas genericos, y el field son extensiones propias de backstage para dar forma y experiencia de plataforma.

Para ello liste los siguientes campos con tipo de datos y el caso de uso de cada uno: 


| Widget / Field | Tipo de dato | Caso de uso |
|---|---|---|
| `text` (por defecto) | `string` | Nombre del servicio, descripción corta. |
| `textarea` | `string` | Descripciones largas o snippets de configuración. |
| `checkbox` | `boolean` | Activar un opcional. |
| `select` (o `enum` en el schema) | `string` con `enum` | Elegir entre valores cerrados: `dev / qa / prod`, `nodejs / java / python`. |
| `radio` | `string` con `enum` | Igual que select, pero con pocas opciones y todas visibles. |
| `password` | `string` | Valores que no deben mostrarse en pantalla. |
| `updown` / `range` | `number`, `integer` | Número de réplicas, puerto, memoria asignada. |
| `checkboxes` | `array` con `enum` | Selección múltiple: features a habilitar. |
| `ui:field: RepoUrlPicker` | `string` | Selector de host + owner + repo para publicar. |
| `ui:field: OwnerPicker` | `string` | Lista buscable de `User`/`Group` **existentes en el catálogo**. |
| `ui:field: EntityPicker` | `string` | Referenciar otra entidad del catálogo (ej. el `System` al que pertenece). |
| `ui:field: Secret` | `string` | Valor sensible; no se persiste en la tarea y se consume con `${{ secrets.X }}` en vez de `${{ parameters.X }}`. |

Propiedades de presentación adicionales: `ui:autofocus`, `ui:help`, `ui:placeholder`,
`ui:emptyValue`, `ui:options` (opciones específicas de cada widget/field).

#### 2.2 Validaciones

¿Cómo puedes hacer que un campo de tipo `string` solo acepte valores en minúsculas sin espacios (útil para nombres de servicios)? Menciona las propiedades de JSON Schema relevantes.

Para este escenario lo mejor y en el template lo utilice, es usar una expresion regilar para ejemplo el nombre del servicio solo en minuscular y sin espacios, acompañada de una longitud maxima, seria algo asi como esto:

```yaml
serviceName:
  title: Nombre del microservicio
  type: string
  description: Solo minúsculas, números y guiones
  pattern: '^[a-z0-9]+(-[a-z0-9]+)*$'
  maxLength: 40
  ui:autofocus: true
  ui:help: 'Ejemplo válido: pagos-api'
```

Si desglosamos la expresion regular, obliga a empezar y terminar con letras minusculas o digito, permite guiones solo si funcionan como separadores, y prohibe los espacios, mayusculas, guiones dobles y guion final.

### 3. Pasos de Orquestación (`steps`)

La sección `steps` define la secuencia de acciones que el scaffolder ejecutará automáticamente.

#### 3.1 Actions disponibles

Investiga las **Built-in Actions** del scaffolder de Backstage. Completa la siguiente tabla con las acciones que necesitarás para tu Golden Path:

Las acciones disponibles serian las siguientes: 

| Action ID | ¿Qué hace? | Inputs principales | Outputs |
|---|---|---|---|
| `fetch:template` | Descarga el directorio *skeleton*, renderiza nombres de archivo y contenidos con Nunjucks usando los `values` recibidos, y deja el resultado en el workspace de la tarea. | `url` (ruta relativa o URL del skeleton), `values` (mapa de variables), `targetPath`, `copyWithoutTemplating` (globs cuyo contenido se copia sin renderizar) | — |
| `fetch:plain` | Copia archivos tal cual, sin procesar plantillas. | `url`, `targetPath` | — |
| `publish:github` | Crea el repositorio remoto en GitHub y hace push del contenido del workspace. Requiere el módulo `scaffolder-backend-module-github` y un token con scope `repo`. | `repoUrl` (`github.com?owner=X&repo=Y`), `description`, `defaultBranch`, `repoVisibility`, `access`, `protectDefaultBranch` | `remoteUrl`, `repoContentsUrl`, `commitHash` |
| `catalog:register` | Registra una `Location` apuntando al `catalog-info.yaml` del repo recién creado, para que el componente aparezca en el Software Catalog. | `repoContentsUrl` + `catalogInfoPath`, o `catalogInfoUrl` | `entityRef`, `catalogInfoUrl` |
| `catalog:write` | Escribe un `catalog-info.yaml` generado dinámicamente en el workspace. | `entity` | — |
| `debug:log` | Imprime mensajes en el log de la tarea. Muy útil para depurar valores. | `message` | — |

Si quisieramos consultarlas lo podriamos hacer desde el `http://localhost/create/actions`.

#### 3.2 Motor de Plantillas (Nunjucks)

El paso `fetch:template` usa **Nunjucks** para reemplazar variables en los archivos del skeleton. ¿Cómo accedes al valor de un parámetro llamado `serviceName` dentro de un archivo del skeleton?

Dentro del Skeleton lo valores pasados por el input.values, se exponen bajo el objeto values, asi: 

```
${{ values.serviceName }}
```

#### 3.3 Output del paso `publish:github`

La acción `publish:github` retorna un output que puedes usar en pasos siguientes. ¿Qué propiedad del output contiene la URL del repositorio recién creado? ¿Cómo se referencia en el siguiente paso?

Los outputs expuestos son:

| Output | Contenido |
|---|---|
| `remoteUrl` | URL del repositorio para humanos (`https://github.com/owner/repo`). Es la que se pone en `output.links`. |
| `repoContentsUrl` | URL al contenido del repo en la rama por defecto. Es la que consume `catalog:register`. |
| `commitHash` | SHA del commit inicial. |

Y se referencian: 

```yaml
- id: register
  name: Registrar en el catálogo
  action: catalog:register
  input:
    repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
    catalogInfoPath: '/catalog-info.yaml'
```

### 4. Outputs del Template

La sección `output` del template permite mostrarle al usuario información al final del proceso (links, instrucciones, etc.).

¿Qué tipos de `links` puedes mostrar en el output? Lista al menos 2 ejemplos concretos para nuestro caso de uso (link al repo, link al componente en el catálogo).

El spec.output admite links y text. Ese link puede apuntar a una URL interna o a una entidad que este dentro del catalogo medienta entityRef, ejemplo:

```yaml
output:
  links:
    - title: Repositorio en GitHub
      url: ${{ steps.publish.output.remoteUrl }}
    - title: Abrir el componente en el catálogo
      icon: catalog
      entityRef: ${{ steps.register.output.entityRef }}
  text:
    - title: Siguientes pasos
      content: |
        git clone ${{ steps.publish.output.remoteUrl }}
```

### 5. El Skeleton del Microservicio

El directorio `skeleton/` contiene la estructura base del proyecto que se copiará como punto de partida. Investiga:

#### 5.1 Parametrización del skeleton

El archivo `skeleton/catalog-info.yaml` también debe parametrizarse. Investiga la estructura del `catalog-info.yaml` de Backstage y responde: ¿Qué campos mínimos son obligatorios?

Los campos minimos son los siguientes: 

| Campo | Obligatorio | Nota |
|---|---|---|
| `apiVersion` | Sí | `backstage.io/v1alpha1` |
| `kind` | Sí | `Component` |
| `metadata.name` | Sí | Único; solo `[a-z0-9A-Z]` más `-`, `_`, `.` (máx. 63 caracteres) |
| `spec.type` | Sí | `service`, `website`, `library`, … |
| `spec.lifecycle` | Sí | `experimental`, `production`, `deprecated` |
| `spec.owner` | Sí | Referencia a un `User` o `Group`; si no existe en el catálogo queda como relación rota |
| `metadata.description`, `metadata.tags`, `metadata.annotations`, `spec.system` | No | Recomendados |

---

## Objetivo: Construir tu Golden Path

Con la investigación completa, tienes todo lo necesario para construir tu Software Template. Tu template debe cumplir los siguientes requisitos:

### Contrato de la API (Parámetros)

El formulario que verá el desarrollador debe pedir **exactamente 2 campos**:

| Campo | Tipo | Descripción |
|---|---|---|
| `serviceName` | `string` | Nombre del microservicio (minúsculas, sin espacios) |
| `owner` | `string` | Propietario del componente (user o group del catálogo) |

### Acciones Orquestadas (Steps)

El template debe ejecutar **exactamente 4 pasos** en este orden:

```
Paso 1: fetch:template
        └── Descarga el skeleton de este repositorio e inyecta los parámetros

Paso 2: publish:github
        └── Crea un nuevo repositorio en tu cuenta personal de GitHub
            y hace push del código generado

Paso 3: catalog:register
        └── Registra el nuevo componente en el Software Catalog de Backstage

(Opcional) Paso 4: Output
        └── Muestra al usuario el link al repo y al componente en el catálogo
```

---

## Cómo cargar tu template en Backstage

Una vez que tengas tu `template.yaml` completo y subido a GitHub:

1. En Backstage, ve a **Settings → Catalog → Add Existing Component**
2. Introduce la URL raw de tu `template.yaml` en GitHub, por ejemplo:
   ```
   https://github.com/tu-usuario/tu-repo/blob/main/golden-path/template.yaml
   ```
3. Backstage descargará el template y lo mostrará en la sección **Create** del portal.
4. Prueba tu Golden Path creando un nuevo microservicio de prueba.
