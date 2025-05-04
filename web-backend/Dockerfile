FROM maven:3.9.6-eclipse-temurin-17-alpine as build
WORKDIR /app
COPY . .
RUN mvn install -DskipTests=true

FROM eclipse-temurin:17-jdk-alpine
WORKDIR /run
COPY --from=build /app/target/web-backend-0.0.1-SNAPSHOT.jar /run/web-backend-0.0.1-SNAPSHOT.jar
EXPOSE 8080
ENTRYPOINT java -jar /run/web-backend-0.0.1-SNAPSHOT.jar