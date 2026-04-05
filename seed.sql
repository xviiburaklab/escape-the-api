INSERT INTO rooms (type, title, clue, answer, hint, room_order, active) VALUES
('cipher', 'The Cipher Room', 'Decode this ROT13 message to find the password: BCRA FRFNZR', 'open sesame', 'ROT13 shifts each letter by 13 positions. A becomes N, B becomes O...', 1, true),
('header', 'The Vault Door', 'The key is hidden in plain sight. Send it encoded in base64 via the x-secret-base header. The key is: skeleton', 'skeleton', 'Base64 encode the answer and put it in the x-secret-base header.', 2, true),
('query_param', 'The Query Gate', 'The gatekeeper only responds to those who ask with the right key. Pass ?key=opensesame in your query.', 'opensesame', 'Add ?key=opensesame to your request URL as a query parameter.', 3, true),
('body_field', 'The Nested Vault', 'The final lock requires a deeply hidden key. Send it as: {"secret": {"key": "freedom"}}', 'freedom', 'Structure your JSON body with a nested object: secret.key', 4, true),
('default', 'The Final Door', 'What is the universal key that opens all doors? (Hint: it is a 4-letter word meaning affection)', 'love', 'Think about what makes the world go round...', 5, true),
('hidden_header', 'The Inspector''s Key', 'Look closely at the server response metadata...', 'chrome-inspect', 'Think about "headers" and your browser''s Network tab.', 6, true);
