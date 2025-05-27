import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

const CryptoCurrencyChart = () => {
  const [chartData, setChartData] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/data/crypto_rates.json');
        const data = await response.json();

        const chartData = {
          labels: data.map(item => item.date),
          datasets: [{
            label: 'Курс BTC/USD',
            data: data.map(item => item.price),
            borderColor: 'rgb(255, 99, 132)',
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
      <h2>Динамика криптовалют</h2>
      {chartData.labels ? (
        <Line data={chartData} />
      ) : (
        <p>Загрузка данных...</p>
      )}
    </div>
  );
};

export default CryptoCurrencyChart;