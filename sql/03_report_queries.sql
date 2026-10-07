-- Consultas de reporte para validar los resultados del bot
USE OrderIntake;
GO

-- 1) Rechazos agrupados por motivo
SELECT reason, COUNT(*) AS total_rechazos
FROM order_exceptions
GROUP BY reason
ORDER BY total_rechazos DESC;
GO

-- 2) Pedidos cargados por día
SELECT order_date, COUNT(*) AS pedidos_cargados, SUM(quantity * unit_price) AS monto_total
FROM orders
GROUP BY order_date
ORDER BY order_date;
GO

-- 3) Resumen de cada corrida del bot
SELECT run_id, started_at, finished_at, status,
       total_processed, total_loaded, total_rejected
FROM bot_runs
ORDER BY run_id DESC;
GO