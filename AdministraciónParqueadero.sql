USE [master]
GO
/****** Object:  Database [AdministracionParqueadero]    Script Date: 6/05/2025 12:09:48 p. m. ******/
CREATE DATABASE [AdministracionParqueadero]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'AdministracionParqueadero', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\AdministracionParqueadero.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'AdministracionParqueadero_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\AdministracionParqueadero_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
ALTER DATABASE [AdministracionParqueadero] SET COMPATIBILITY_LEVEL = 160
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [AdministracionParqueadero].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [AdministracionParqueadero] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET ARITHABORT OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [AdministracionParqueadero] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [AdministracionParqueadero] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET  DISABLE_BROKER 
GO
ALTER DATABASE [AdministracionParqueadero] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [AdministracionParqueadero] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET RECOVERY SIMPLE 
GO
ALTER DATABASE [AdministracionParqueadero] SET  MULTI_USER 
GO
ALTER DATABASE [AdministracionParqueadero] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [AdministracionParqueadero] SET DB_CHAINING OFF 
GO
ALTER DATABASE [AdministracionParqueadero] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [AdministracionParqueadero] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [AdministracionParqueadero] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [AdministracionParqueadero] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
ALTER DATABASE [AdministracionParqueadero] SET QUERY_STORE = ON
GO
ALTER DATABASE [AdministracionParqueadero] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [AdministracionParqueadero]
GO
/****** Object:  Table [dbo].[Puesto]    Script Date: 6/05/2025 12:09:49 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Puesto](
	[IdPuesto] [int] NOT NULL,
	[Disponible] [bit] NULL,
 CONSTRAINT [PK_Puesto] PRIMARY KEY CLUSTERED 
(
	[IdPuesto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[RegistroParqueo]    Script Date: 6/05/2025 12:09:49 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[RegistroParqueo](
	[IdRegistro] [int] IDENTITY(1,1) NOT NULL,
	[Placa] [nvarchar](10) NOT NULL,
	[IdPuesto] [int] NOT NULL,
	[HoraEntrada] [datetime] NOT NULL,
	[HoraSalida] [datetime] NULL,
	[ValorTarifaAplicada] [decimal](10, 2) NOT NULL,
	[TotalPagado] [decimal](10, 2) NULL,
	[IdTarifa] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[IdRegistro] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Tarifa]    Script Date: 6/05/2025 12:09:49 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Tarifa](
	[IdTarifa] [int] NOT NULL,
	[ValorPorHora] [decimal](10, 2) NULL,
	[FechaInicioVigencia] [datetime] NOT NULL,
	[FechaFinVigencia] [datetime] NULL,
 CONSTRAINT [PK_Tarifa] PRIMARY KEY CLUSTERED 
(
	[IdTarifa] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Vehiculo]    Script Date: 6/05/2025 12:09:49 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Vehiculo](
	[Placa] [nvarchar](10) NOT NULL,
	[Marca] [nvarchar](50) NULL,
	[Modelo] [nvarchar](50) NULL,
 CONSTRAINT [PK_Vehiculo] PRIMARY KEY CLUSTERED 
(
	[Placa] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Index [IX_RegistroParqueo_HoraSalida_NULL]    Script Date: 6/05/2025 12:09:49 p. m. ******/
CREATE NONCLUSTERED INDEX [IX_RegistroParqueo_HoraSalida_NULL] ON [dbo].[RegistroParqueo]
(
	[HoraSalida] ASC
)
WHERE ([HoraSalida] IS NULL)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_RegistroParqueo_IdPuesto]    Script Date: 6/05/2025 12:09:49 p. m. ******/
CREATE NONCLUSTERED INDEX [IX_RegistroParqueo_IdPuesto] ON [dbo].[RegistroParqueo]
(
	[IdPuesto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_RegistroParqueo_IdTarifa]    Script Date: 6/05/2025 12:09:49 p. m. ******/
CREATE NONCLUSTERED INDEX [IX_RegistroParqueo_IdTarifa] ON [dbo].[RegistroParqueo]
(
	[IdTarifa] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_RegistroParqueo_Placa]    Script Date: 6/05/2025 12:09:49 p. m. ******/
CREATE NONCLUSTERED INDEX [IX_RegistroParqueo_Placa] ON [dbo].[RegistroParqueo]
(
	[Placa] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_RegistroParqueo_Puesto]    Script Date: 6/05/2025 12:09:49 p. m. ******/
CREATE NONCLUSTERED INDEX [IX_RegistroParqueo_Puesto] ON [dbo].[RegistroParqueo]
(
	[IdPuesto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[RegistroParqueo]  WITH CHECK ADD  CONSTRAINT [FK_RegistroParqueo_Puesto] FOREIGN KEY([IdPuesto])
REFERENCES [dbo].[Puesto] ([IdPuesto])
GO
ALTER TABLE [dbo].[RegistroParqueo] CHECK CONSTRAINT [FK_RegistroParqueo_Puesto]
GO
ALTER TABLE [dbo].[RegistroParqueo]  WITH CHECK ADD  CONSTRAINT [FK_RegistroParqueo_Tarifa] FOREIGN KEY([IdTarifa])
REFERENCES [dbo].[Tarifa] ([IdTarifa])
GO
ALTER TABLE [dbo].[RegistroParqueo] CHECK CONSTRAINT [FK_RegistroParqueo_Tarifa]
GO
ALTER TABLE [dbo].[RegistroParqueo]  WITH CHECK ADD  CONSTRAINT [FK_RegistroParqueo_Vehiculo] FOREIGN KEY([Placa])
REFERENCES [dbo].[Vehiculo] ([Placa])
GO
ALTER TABLE [dbo].[RegistroParqueo] CHECK CONSTRAINT [FK_RegistroParqueo_Vehiculo]
GO
ALTER TABLE [dbo].[RegistroParqueo]  WITH CHECK ADD  CONSTRAINT [CK_Horarios_Parqueo] CHECK  (([HoraEntrada]<=isnull([HoraSalida],'9999-12-31') AND (CONVERT([time],[HoraEntrada])>='06:00' AND CONVERT([time],[HoraEntrada])<='21:00')))
GO
ALTER TABLE [dbo].[RegistroParqueo] CHECK CONSTRAINT [CK_Horarios_Parqueo]
GO
ALTER TABLE [dbo].[RegistroParqueo]  WITH CHECK ADD  CONSTRAINT [CK_RegistroParqueo_HoraEntradaSalida] CHECK  (([HoraEntrada]<=isnull([HoraSalida],'9999-12-31') AND (CONVERT([time],[HoraEntrada])>='06:00' AND CONVERT([time],[HoraEntrada])<='21:00')))
GO
ALTER TABLE [dbo].[RegistroParqueo] CHECK CONSTRAINT [CK_RegistroParqueo_HoraEntradaSalida]
GO
ALTER TABLE [dbo].[Vehiculo]  WITH CHECK ADD  CONSTRAINT [CK_Formato_Placa] CHECK  (([Placa] like '[A-Z][A-Z][A-Z][0-9][0-9][0-9]' OR [Placa] like '[A-Z][A-Z][0-9][0-9][0-9][A-Z]' OR [Placa] like '[0-9][0-9][0-9][A-Z][A-Z][A-Z]'))
GO
ALTER TABLE [dbo].[Vehiculo] CHECK CONSTRAINT [CK_Formato_Placa]
GO
ALTER TABLE [dbo].[Vehiculo]  WITH CHECK ADD  CONSTRAINT [CK_Vehiculo_FormatoPlaca] CHECK  (([Placa] like '[A-Z][A-Z][A-Z][0-9][0-9][0-9]' OR [Placa] like '[A-Z][A-Z][0-9][0-9][0-9][A-Z]' OR [Placa] like '[0-9][0-9][0-9][A-Z][A-Z][A-Z]'))
GO
ALTER TABLE [dbo].[Vehiculo] CHECK CONSTRAINT [CK_Vehiculo_FormatoPlaca]
GO
/****** Object:  Trigger [dbo].[TR_RegistroParqueo_AfterInsert_ActualizarPuesto]    Script Date: 6/05/2025 12:09:49 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TRIGGER [dbo].[TR_RegistroParqueo_AfterInsert_ActualizarPuesto]
ON [dbo].[RegistroParqueo]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Verificar si el puesto existe y está disponible antes de la inserción
    -- (Esto idealmente se valida en el procedimiento almacenado que hace el INSERT)
    -- Aquí actualizamos el estado del puesto a No Disponible (0)
    UPDATE P
    SET P.Disponible = 0 -- 0 para No Disponible
    FROM dbo.Puesto P
    INNER JOIN inserted I ON P.IdPuesto = I.IdPuesto;

    -- Consideraciones adicionales:
    -- Podrías añadir una verificación aquí para asegurar que el puesto
    -- no estuviera ya ocupado por otro vehículo activo, aunque el índice
    -- UQ_Puesto_ActualmenteOcupado ayudaría a prevenirlo a nivel de BD.
END;
GO
ALTER TABLE [dbo].[RegistroParqueo] ENABLE TRIGGER [TR_RegistroParqueo_AfterInsert_ActualizarPuesto]
GO
/****** Object:  Trigger [dbo].[TR_RegistroParqueo_AfterUpdate_ActualizarPuesto]    Script Date: 6/05/2025 12:09:49 p. m. ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TRIGGER [dbo].[TR_RegistroParqueo_AfterUpdate_ActualizarPuesto]
ON [dbo].[RegistroParqueo]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Solo actuar si HoraSalida ha sido actualizada (y no era NULL antes o cambió a un valor no NULL)
    IF UPDATE(HoraSalida)
    BEGIN
        UPDATE P
        SET P.Disponible = 1 -- 1 para Disponible
        FROM dbo.Puesto P
        INNER JOIN inserted I ON P.IdPuesto = I.IdPuesto
        INNER JOIN deleted D ON I.IdRegistro = D.IdRegistro
        WHERE I.HoraSalida IS NOT NULL AND D.HoraSalida IS NULL; -- Asegurarse que la salida se acaba de registrar
    END
END;
GO
ALTER TABLE [dbo].[RegistroParqueo] ENABLE TRIGGER [TR_RegistroParqueo_AfterUpdate_ActualizarPuesto]
GO
USE [master]
GO
ALTER DATABASE [AdministracionParqueadero] SET  READ_WRITE 
GO
