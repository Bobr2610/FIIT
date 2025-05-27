import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

const FiatCurrencyChart = () => {
  const [chartData, setChartData] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/data/aed_rub_5year_rates_2025-05-20.json');
        const data = await response.json();

        const chartData = {
          labels: data.map(item => item.date),
          datasets: [{
            label: 'Курс AED/RUB',
            data: data.map(item => item.price),
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
          }]
        };

        setChartData(chartData);
      } catch (error) {
        console.error('Ошибка загрузки данных:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h2>Динамика фиатных валют</h2>
      {chartData.labels ? (
        <Line data={chartData} />
      ) : (
        <p>Загрузка данных...</p>
      )}
    </div>
  );
};

export default FiatCurrencyChart;