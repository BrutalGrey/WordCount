# WordCount
Подсчет количества слов.
В Docker создаются контейнеры: spark, cassandra, kafka, zookeeper.
Скрипт Main.py читает из kafka, подсчитывает количество повторений и записывает данные в Cassandra.
В файле Commands.txt указаны команды для обращения к Cassandra(cassandra-server) и к Kafka.produser(kafka-server).
