CREATE TABLE `post` (
  `id` int(11) NOT NULL,
  `content` text,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
