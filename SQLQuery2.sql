USE GimnasioDB;
GO

-- 1. Insertar tipos de planes
INSERT INTO Planes (Nombre, Precio, DuracionDias) VALUES 
('Mensual Básico', 80.00, 30),
('Trimestral Pro', 210.00, 90),
('Anual VIP', 750.00, 365);
GO

-- 2. Insertar socios vinculados a un plan
INSERT INTO Socios (Dni, Nombre, Apellido, IdPlan, Estado) VALUES 
('72345678', 'Mateo', 'Rivas', 1, 'Activo'),
('78912345', 'Valeria', 'Gómez', 2, 'Activo'),
('70123456', 'Jorge', 'Herrera', 1, 'Inactivo');
GO

-- 3. Consultar y unir las dos tablas
SELECT 
    s.IdSocio,
    s.Dni,
    s.Nombre + ' ' + s.Apellido AS Socio,
    p.Nombre AS PlanElegido,
    p.Precio,
    s.Estado
FROM Socios s
INNER JOIN Planes p ON s.IdPlan = p.IdPlan;
GO