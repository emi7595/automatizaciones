-- WhatsApp Automation MVP Database Schema
-- This file contains the complete SQL schema for the MVP

-- Enable UUID extension for conversation IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Celery tables for background task processing (Render compatibility)
CREATE TABLE celery_taskmeta (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    result JSONB,
    date_done TIMESTAMP WITH TIME ZONE,
    traceback TEXT,
    hidden BOOLEAN NOT NULL DEFAULT false,
    meta JSONB
);

CREATE TABLE celery_tasksetmeta (
    id SERIAL PRIMARY KEY,
    taskset_id VARCHAR(255) UNIQUE NOT NULL,
    result JSONB,
    date_done TIMESTAMP WITH TIME ZONE
);

-- Create indexes for Celery tables
CREATE INDEX idx_celery_taskmeta_task_id ON celery_taskmeta(task_id);
CREATE INDEX idx_celery_taskmeta_status ON celery_taskmeta(status);
CREATE INDEX idx_celery_taskmeta_hidden ON celery_taskmeta(hidden);
CREATE INDEX idx_celery_tasksetmeta_taskset_id ON celery_tasksetmeta(taskset_id);

-- Users table for authentication and authorization
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Enhanced contacts table with comprehensive metadata
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100),
    birthday DATE,
    tags JSONB,
    notes TEXT,
    last_contacted TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by INTEGER NOT NULL REFERENCES users(id)
);

-- Create indexes for contacts
CREATE INDEX idx_contacts_phone ON contacts(phone);
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_birthday ON contacts(birthday);
CREATE INDEX idx_contacts_created_by ON contacts(created_by);
CREATE INDEX idx_contacts_is_active ON contacts(is_active);
CREATE INDEX idx_contacts_tags ON contacts USING GIN(tags);

-- Messages table with threading support
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id),
    conversation_id VARCHAR(36) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('inbound', 'outbound')),
    message_type VARCHAR(20) NOT NULL DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'document', 'audio', 'video', 'template')),
    content TEXT NOT NULL,
    whatsapp_message_id VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'failed')),
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

-- Create indexes for messages
CREATE INDEX idx_messages_contact_id ON messages(contact_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_direction ON messages(direction);
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_whatsapp_id ON messages(whatsapp_message_id);
CREATE INDEX idx_messages_metadata ON messages USING GIN(metadata);

-- Automations table with flexible configuration
CREATE TABLE automations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(20) NOT NULL CHECK (trigger_type IN ('new_contact', 'birthday', 'message_received', 'scheduled', 'keyword', 'time_based', 'manual')),
    trigger_conditions JSONB,
    action_type VARCHAR(30) NOT NULL CHECK (action_type IN ('send_message', 'add_to_group', 'update_contact', 'trigger_automation', 'send_email', 'log_activity')),
    action_payload JSONB NOT NULL,
    schedule_config JSONB,
    is_active BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 1 CHECK (priority BETWEEN 1 AND 10),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_by INTEGER NOT NULL REFERENCES users(id)
);

-- Create indexes for automations
CREATE INDEX idx_automations_trigger_type ON automations(trigger_type);
CREATE INDEX idx_automations_action_type ON automations(action_type);
CREATE INDEX idx_automations_is_active ON automations(is_active);
CREATE INDEX idx_automations_priority ON automations(priority);
CREATE INDEX idx_automations_created_by ON automations(created_by);
CREATE INDEX idx_automations_trigger_conditions ON automations USING GIN(trigger_conditions);
CREATE INDEX idx_automations_action_payload ON automations USING GIN(action_payload);

-- Automation logs for tracking execution
CREATE TABLE automation_logs (
    id SERIAL PRIMARY KEY,
    automation_id INTEGER NOT NULL REFERENCES automations(id),
    contact_id INTEGER REFERENCES contacts(id),
    execution_status VARCHAR(20) NOT NULL CHECK (execution_status IN ('success', 'failed', 'partial', 'skipped')),
    execution_time FLOAT,
    contacts_affected INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    execution_details JSONB,
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    executed_by VARCHAR(50) NOT NULL DEFAULT 'system'
);

-- Create indexes for automation logs
CREATE INDEX idx_automation_logs_automation_id ON automation_logs(automation_id);
CREATE INDEX idx_automation_logs_contact_id ON automation_logs(contact_id);
CREATE INDEX idx_automation_logs_status ON automation_logs(execution_status);
CREATE INDEX idx_automation_logs_executed_at ON automation_logs(executed_at);
CREATE INDEX idx_automation_logs_execution_details ON automation_logs USING GIN(execution_details);

-- Analytics table for comprehensive metrics
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    metric_type VARCHAR(30) NOT NULL CHECK (metric_type IN ('message_delivery', 'automation_performance', 'contact_engagement', 'system_performance', 'user_activity')),
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    dimensions JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE
);

-- Create indexes for analytics
CREATE INDEX idx_analytics_metric_type ON analytics(metric_type);
CREATE INDEX idx_analytics_metric_name ON analytics(metric_name);
CREATE INDEX idx_analytics_recorded_at ON analytics(recorded_at);
CREATE INDEX idx_analytics_period_start ON analytics(period_start);
CREATE INDEX idx_analytics_dimensions ON analytics USING GIN(dimensions);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_automations_updated_at BEFORE UPDATE ON automations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, full_name, hashed_password, role) 
VALUES ('admin', 'admin@automatizaciones.com', 'System Administrator', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.8K2O', 'admin');

-- Insert sample contacts for testing
INSERT INTO contacts (name, phone, email, birthday, tags, notes, created_by) VALUES
('Juan Pérez', '+1234567890', 'juan@example.com', '1990-05-15', '["vip", "premium"]', 'Important client', 1),
('María García', '+1234567891', 'maria@example.com', '9999-03-20', '["regular"]', 'Birthday unknown year', 1),
('Carlos López', '+1234567892', 'carlos@example.com', '1985-12-10', '["vip"]', 'Long-time customer', 1);

-- Insert sample automations
INSERT INTO automations (name, description, trigger_type, trigger_conditions, action_type, action_payload, created_by) VALUES
('Welcome New Contact', 'Send welcome message to new contacts', 'new_contact', '{}', 'send_message', 
 '{"message_template": "¡Hola {name}! Bienvenido a nuestro servicio. ¿En qué podemos ayudarte?", "delay_seconds": 5}', 1),
('Birthday Greeting', 'Send birthday message to contacts', 'birthday', '{}', 'send_message', 
 '{"message_template": "¡Feliz cumpleaños {name}! 🎉 Que tengas un día maravilloso.", "delay_seconds": 0}', 1);

-- Insert sample analytics
INSERT INTO analytics (metric_type, metric_name, metric_value, dimensions) VALUES
('system_performance', 'total_contacts', 3, '{"period": "all_time"}'),
('system_performance', 'total_automations', 2, '{"period": "all_time"}'),
('system_performance', 'active_automations', 2, '{"period": "current"}');
