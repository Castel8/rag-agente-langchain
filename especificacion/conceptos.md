Explicacion API REST, componentes y servicios

1. Una API REST es una interfaz de programación de Aplicaciones, en la que un programa pregunta y solicita cosas a otro por medio de internet, usando direcciones o enalces web. Ejemplo de la vida cotidiano: Piensa que estamos en un restaurante, el mesero es la (API), tú (el cliente) haces un pedido de comida, la cocina en donde se prepara el pedido (el servidor) lo prepara y el mesero te trae la respuesta.
2. Cada dirección por donde pasa la informacion se llama endpoint, por ejemplo /predict.
3. GET es un comando que sirve para consultar algo. POST es otro comando pero que sirve para enviar datos que el servidor debe procesar.
4. Cada respuesta trae un código de estado, como un numero que categoriza la ejecucion correcta o con falla de un proceso: 200 todo bien, 400 o 422 datos mal enviados, 404 no existe lo que pediste y 500 falló el servidor.
5. Los datos viajan en formato JSON, un texto que tiene una estructura de nombre-valor, asi como un diccionario en pyhton clave: valor, el formato JSON lo puede entender cualquier lenguaje de programacion.
6. Un microservicio es un servicio pequeño que se centra en ejecutar un proceso en buenas condiciones. El nuestro expondrá el modelo y el RAG.