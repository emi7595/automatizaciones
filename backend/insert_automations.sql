-- Insert automation triggers for existing users
-- Run these queries to add automation triggers to your database

-- 1. Welcome Back Message for Existing Users
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Welcome Back - Existing Users',
    'Sends a welcome back message to existing users when they send a message',
    'message_received',
    '{
        "hours": 24,
        "sender_criteria": {
            "min_messages": 1,
            "existing_contact": true
        }
    }',
    'send_message',
    '{
        "message": "Welcome back! How can I help you today?",
        "message_type": "text"
    }',
    true,
    1,
    1
);

-- 2. Help Keyword Automation
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Help Keyword Response',
    'Responds to help requests from any user',
    'keyword',
    '{
        "keywords": ["help", "support", "assistance", "ayuda"],
        "case_sensitive": false,
        "exact_match": false
    }',
    'send_message',
    '{
        "message": "Hi! I''m here to help. What do you need assistance with?",
        "message_type": "text"
    }',
    true,
    2,
    1
);

-- 3. Pricing Information Request
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Pricing Information',
    'Provides pricing information when requested',
    'keyword',
    '{
        "keywords": ["price", "pricing", "cost", "precio", "costo"],
        "case_sensitive": false,
        "exact_match": false
    }',
    'send_message',
    '{
        "message": "Here are our current pricing options:\n\n• Basic Plan: $29/month\n• Pro Plan: $59/month\n• Enterprise: Custom pricing\n\nWould you like more details about any of these plans?",
        "message_type": "text"
    }',
    true,
    3,
    1
);

-- 4. Contact Information Request
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Contact Information',
    'Provides contact information when requested',
    'keyword',
    '{
        "keywords": ["contact", "phone", "email", "address", "direccion"],
        "case_sensitive": false,
        "exact_match": false
    }',
    'send_message',
    '{
        "message": "You can reach us at:\n\n📞 Phone: +1-555-0123\n📧 Email: info@company.com\n🏢 Address: 123 Business St, City, State\n\nWe''re available Monday-Friday 9AM-6PM",
        "message_type": "text"
    }',
    true,
    4,
    1
);

-- 5. VIP Customer Priority Response
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'VIP Customer Response',
    'Special response for VIP customers',
    'keyword',
    '{
        "keywords": ["urgent", "priority", "asap", "urgente"],
        "case_sensitive": false,
        "exact_match": false,
        "sender_criteria": {
            "tags": ["vip", "premium"]
        }
    }',
    'send_message',
    '{
        "message": "Hi! As a VIP customer, I''ll prioritize your request. What do you need?",
        "message_type": "text"
    }',
    true,
    1,
    1
);

-- 6. Thank You Response
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Thank You Response',
    'Responds to thank you messages',
    'keyword',
    '{
        "keywords": ["thanks", "thank you", "gracias", "appreciate"],
        "case_sensitive": false,
        "exact_match": false
    }',
    'send_message',
    '{
        "message": "You''re very welcome! Is there anything else I can help you with?",
        "message_type": "text"
    }',
    true,
    5,
    1
);

-- 7. General Greeting Response
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Greeting Response',
    'Responds to general greetings',
    'keyword',
    '{
        "keywords": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
        "case_sensitive": false,
        "exact_match": false
    }',
    'send_message',
    '{
        "message": "Hello! How can I assist you today?",
        "message_type": "text"
    }',
    true,
    6,
    1
);

-- 8. Log Activity for All Messages
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Log All Message Activity',
    'Logs activity for all incoming messages',
    'message_received',
    '{
        "hours": 24
    }',
    'log_activity',
    '{
        "activity_type": "message_received",
        "description": "User sent a message",
        "metadata": {
            "auto_logged": true,
            "source": "automation"
        }
    }',
    true,
    10,
    1
);

-- 9. Update Last Contacted for Existing Users
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Update Contact Activity',
    'Updates contact information when existing users message',
    'message_received',
    '{
        "hours": 24,
        "sender_criteria": {
            "min_messages": 1
        }
    }',
    'update_contact',
    '{
        "update_fields": {
            "last_contacted": "now",
            "interaction_count": "increment"
        },
        "add_tags": ["active_user"],
        "notes": "User sent a message - last contacted updated"
    }',
    true,
    7,
    1
);

-- 10. Business Hours Response
INSERT INTO automations (
    name, 
    description, 
    trigger_type, 
    trigger_conditions, 
    action_type, 
    action_payload, 
    is_active, 
    priority, 
    created_by
) VALUES (
    'Business Hours Information',
    'Provides business hours information',
    'keyword',
    '{
        "keywords": ["hours", "schedule", "time", "open", "closed", "horario"],
        "case_sensitive": false,
        "exact_match": false
    }',
    'send_message',
    '{
        "message": "Our business hours are:\n\n🕘 Monday - Friday: 9:00 AM - 6:00 PM\n🕘 Saturday: 10:00 AM - 4:00 PM\n🕘 Sunday: Closed\n\nWe''ll respond to your message during business hours!",
        "message_type": "text"
    }',
    true,
    8,
    1
);
