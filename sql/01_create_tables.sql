IF DB_ID('OrderIntake') IS NULL
    CREATE DATABASE OrderIntake;
GO

USE OrderIntake;
GO

-- Catálogo de productos
CREATE TABLE products (
    sku         VARCHAR(20)   NOT NULL,
    name        NVARCHAR(100) NOT NULL,
    list_price  DECIMAL(10,2) NOT NULL,
    CONSTRAINT PK_products PRIMARY KEY (sku),
    CONSTRAINT CK_products_price CHECK (list_price > 0)
);

-- Métricas de cada corrida del bot
CREATE TABLE bot_runs (
    run_id           INT IDENTITY(1,1) NOT NULL,
    started_at       DATETIME2         NOT NULL DEFAULT SYSDATETIME(),
    finished_at      DATETIME2         NULL,
    total_processed  INT               NOT NULL DEFAULT 0,
    total_loaded     INT               NOT NULL DEFAULT 0,
    total_rejected   INT               NOT NULL DEFAULT 0,
    status           VARCHAR(20)       NOT NULL DEFAULT 'RUNNING',
    CONSTRAINT PK_bot_runs PRIMARY KEY (run_id),
    CONSTRAINT CK_bot_runs_status CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED'))
);

-- Pedidos válidos
CREATE TABLE orders (
    order_id        VARCHAR(20)   NOT NULL,
    customer_email  VARCHAR(150)  NOT NULL,
    sku             VARCHAR(20)   NOT NULL,
    quantity        INT           NOT NULL,
    order_date      DATE          NOT NULL,
    unit_price      DECIMAL(10,2) NOT NULL,
    run_id          INT           NOT NULL,
    loaded_at       DATETIME2     NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT PK_orders PRIMARY KEY (order_id),
    CONSTRAINT FK_orders_products FOREIGN KEY (sku) REFERENCES products (sku),
    CONSTRAINT FK_orders_runs FOREIGN KEY (run_id) REFERENCES bot_runs (run_id),
    CONSTRAINT CK_orders_quantity CHECK (quantity > 0),
    CONSTRAINT CK_orders_price CHECK (unit_price > 0)
);

-- Pedidos rechazados con su motivo
CREATE TABLE order_exceptions (
    exception_id  INT IDENTITY(1,1) NOT NULL,
    run_id        INT               NOT NULL,
    order_id      VARCHAR(50)       NULL,
    raw_row       NVARCHAR(500)     NULL,
    reason        NVARCHAR(300)     NOT NULL,
    created_at    DATETIME2         NOT NULL DEFAULT SYSDATETIME(),
    CONSTRAINT PK_order_exceptions PRIMARY KEY (exception_id),
    CONSTRAINT FK_exceptions_runs FOREIGN KEY (run_id) REFERENCES bot_runs (run_id)
);
GO