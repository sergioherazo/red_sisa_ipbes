-- Red SISA · Mapa IPBES
-- Pega todo este archivo en Supabase > SQL Editor > Run.

create table if not exists public.respuestas (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  semillero text not null check (char_length(semillero) between 2 and 200),
  semillero_otro boolean not null default false,          -- true si no estaba en la lista
  principal text not null check (principal in (
    'naturaleza','contribuciones','calidad_vida','activos','instituciones',
    'motores_antropogenicos','motores_naturales','socioecologicos')),
  secundarias text[] not null default '{}' check (cardinality(secundarias) <= 3),
  motivo text check (motivo is null or char_length(motivo) <= 280),
  contacto_nombre text check (contacto_nombre is null or char_length(contacto_nombre) <= 120),
  contacto_correo text check (contacto_correo is null or char_length(contacto_correo) <= 120)
);

-- Quien abre el QR solo puede ENVIAR respuestas: no puede leer, editar ni borrar la tabla.
alter table public.respuestas enable row level security;
drop policy if exists "enviar respuestas" on public.respuestas;
create policy "enviar respuestas" on public.respuestas
  for insert to anon with check (true);
revoke all on public.respuestas from anon;
grant insert on public.respuestas to anon;

-- Vista pública para la pestaña "Resultados": la última respuesta de cada semillero,
-- sin nombre ni correo de contacto.
create or replace view public.respuestas_actuales as
  select distinct on (semillero)
         semillero, semillero_otro, principal, secundarias, motivo, created_at
  from public.respuestas
  order by semillero, created_at desc;
grant select on public.respuestas_actuales to anon;
