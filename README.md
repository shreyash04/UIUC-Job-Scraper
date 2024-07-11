<a name="readme-top"></a>

<h1 align="center">UIUC Job Scraper</h1>

### Built With
[![Google Cloud][gcp-logo]][gcp-url]
<a href="https://airflow.apache.org/" style="text-decoration: none; margin-right: 10px;"><img src="https://github.com/apache/airflow/blob/main/airflow/www/static/pin_100.png?raw=true" alt="Airflow" style="height: 46px;"></a>
<a href="https://www.mongodb.com/products/platform/atlas-database"><img src="https://flowygo.com/wp-content/uploads/2020/12/mongodb-atlas-1024x338.png" alt="MongoDB" style="height: 68px;"></a>
[![Python][python-logo]][python-url]
<a href="https://beautiful-soup-4.readthedocs.io/"><img src="https://editor.analyticsvidhya.com/uploads/82659bs4.PNG" alt="BeutifulSoup" style="height: 48px;"></a>

[gcp-logo]:https://img.icons8.com/color/48/google-cloud.png
[gcp-url]: https://cloud.google.com/
[python-logo]: https://img.icons8.com/color/48/000000/python.png
[python-url]: https://www.python.org

#### Google Compute Engine VM Instance Configuration


<ul>
    <li>For this project, we utilized a GCP VM Spot Instance to host the local Airflow instance. The chosen configuration was a General Purpose e2-medium for cost-effectiveness.</li>
    <li>Initially, we attempted to leverage GCP's Cloud Composer, a managed orchestration tool and equivalent to Airflow. However, there were configuration challenges with Cloud Composer for economical Compute Engine instances, so we used a locally hosted Airflow instance.</li>
    <li>From instance configuration experiences, we recommend using at least an e2-medium machine to ensure smooth operation of Airflow. This configuration provides adequate computational resources to handle the orchestration tasks efficiently.</li>
</ul>


### Airflow Interface
<img src="Airflow DAGs.png">

### DAGs Orchestration Graph
<img src="DAGs Orchestration Graph.png">

### MongoDB Database Backend
<img src="MongoDB Database.png">

<p align="right"><a href="#readme-top">back to top</a></p>


