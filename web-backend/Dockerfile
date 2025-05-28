FROM maven:3.9.6-eclipse-temurin-17-alpine as build
WORKDIR /src
COPY . .
RUN mvn install -DskipTests=true

FROM eclipse-temurin:17-jdk-alpine
COPY --from=build /src/target/web-backend-0.0.1-SNAPSHOT.jar /run/web-backend-0.0.1-SNAPSHOT.jar
RUN mkdir -p /run/config
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/run/web-backend-0.0.1-SNAPSHOT.jar"]
# ENTRYPOINT ["java", "-jar", "/run/web-backend-0.0.1-SNAPSHOT.jar", "--spring.config.location=/run/config/application.properties"]