-- Carga el catálogo inicial de 20 productos
USE OrderIntake;
GO

INSERT INTO products (sku, name, list_price) VALUES
('SKU-001', N'Cuaderno rayado A4',        2.50),
('SKU-002', N'Lapicero azul',             0.80),
('SKU-003', N'Lapicero negro',            0.80),
('SKU-004', N'Resaltador amarillo',       1.20),
('SKU-005', N'Carpeta de manila',         0.60),
('SKU-006', N'Grapadora metálica',        6.90),
('SKU-007', N'Caja de grapas',            1.50),
('SKU-008', N'Tijeras de oficina',        3.40),
('SKU-009', N'Pegamento en barra',        1.10),
('SKU-010', N'Cinta adhesiva',            1.30),
('SKU-011', N'Calculadora básica',       12.00),
('SKU-012', N'Mochila escolar',          24.90),
('SKU-013', N'Estuche de lápices',        4.75),
('SKU-014', N'Regla de 30 cm',            0.95),
('SKU-015', N'Block de notas adhesivas',  2.20),
('SKU-016', N'Marcador permanente',       1.60),
('SKU-017', N'Papel bond resma',          7.80),
('SKU-018', N'Agenda 2026',               9.50),
('SKU-019', N'Perforadora de 2 huecos',   8.30),
('SKU-020', N'Archivador de palanca',     5.40);
GO

SELECT COUNT(*) AS total_productos FROM products;
GO