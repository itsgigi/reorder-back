# 🔧 Supabase su Vercel - Guida Completa

## ⚠️ PROBLEMA: Stai usando la connessione sbagliata!

Se vedi questo errore:
```
Cannot assign requested address
connection to server at "db.xxx.supabase.co" (2a05:d018:...), port 5432 failed
```

**Causa**: Stai usando la **Direct Connection** (porta 5432) invece del **Connection Pooler** (porta 6543).

## ✅ SOLUZIONE: Usa il Connection Pooler

### STEP 1: Vai su Supabase Dashboard

1. Vai su [supabase.com](https://supabase.com)
2. Accedi al tuo progetto
3. Vai su **Settings** (icona ingranaggio in basso a sinistra)
4. Clicca su **Database** nel menu laterale

### STEP 2: Trova il Connection Pooler

1. Scorri fino a **"Connection Pooling"**
2. Vedrai una sezione con **"Connection String"**
3. **NON usare** la "Direct connection" (porta 5432)
4. **USA** la connection string del **Connection Pooler** (porta 6543)

### STEP 3: Copia la Connection String Corretta

Dovresti vedere qualcosa come:

```
postgresql://postgres.xxx:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**Nota importante**:
- ✅ Porta **6543** (Connection Pooler) ← USA QUESTA!
- ❌ Porta **5432** (Direct Connection) ← NON FUNZIONA SU VERCEL!

### STEP 4: Configura Vercel

1. Vai su [vercel.com](https://vercel.com) → il tuo progetto
2. **Settings** → **Environment Variables**
3. Trova `DATABASE_URL` o creane una nuova
4. **Sostituisci** il valore con la connection string del **Connection Pooler** (porta 6543)
5. Clicca **Save**

### STEP 5: Riavvia il Deployment

1. Vai su **Deployments**
2. Clicca sui **3 puntini** (⋮) sull'ultimo deployment
3. Clicca **"Redeploy"**
4. Attendi 2-3 minuti

## 📋 Formato Connection String Corretto

### ❌ SBAGLIATO (Direct Connection - NON funziona su Vercel):
```
postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres
                                                      ^^^^
                                                      Porta 5432
```

### ✅ CORRETTO (Connection Pooler - Funziona su Vercel):
```
postgresql://postgres.xxx:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
                                                                          ^^^^
                                                                          Porta 6543
```

**Differenze chiave**:
- Host: `pooler.supabase.com` (non `db.xxx.supabase.co`)
- Porta: `6543` (non `5432`)
- User: `postgres.xxx` (non solo `postgres`)

## 🔄 Conversione Automatica

Il codice converte automaticamente la porta 5432 → 6543, ma:
- ⚠️ **Non cambia l'host** (devi usare `pooler.supabase.com`)
- ⚠️ **Non cambia l'utente** (devi usare `postgres.xxx`)

**Quindi è meglio usare direttamente il Connection Pooler!**

## 🎯 Checklist

- [ ] Vai su Supabase → Settings → Database → Connection Pooling
- [ ] Copiato la connection string del **Connection Pooler** (porta 6543)
- [ ] Verificato che l'host sia `pooler.supabase.com` (non `db.xxx.supabase.co`)
- [ ] Verificato che la porta sia `6543` (non `5432`)
- [ ] Aggiornato `DATABASE_URL` in Vercel con la connection string corretta
- [ ] Riavviato il deployment
- [ ] Verificato che funzioni: `curl https://your-app.vercel.app/api/health`

## 🆘 Se Ancora Non Funziona

### Opzione 1: Usa Neon (Più Semplice)

Neon funziona meglio con Vercel e non ha problemi IPv6:
1. Vai su [neon.tech](https://neon.tech)
2. Crea un progetto
3. Copia la connection string
4. Usala in Vercel

Vedi [SETUP_VERCEL.md](SETUP_VERCEL.md) per i dettagli.

### Opzione 2: Verifica la Connection String

Assicurati che la connection string:
1. Usi la porta **6543**
2. Usi l'host `pooler.supabase.com`
3. Non contenga parametri `pgbouncer=true`
4. Contenga `sslmode=require` (opzionale ma consigliato)

### Opzione 3: Controlla i Log

1. Vai su Vercel → Deployments → Logs
2. Cerca errori di connessione
3. Verifica che la porta sia 6543 nei log

## 📝 Note Importanti

- **Direct Connection (5432)**: Funziona solo su server tradizionali (non Vercel/serverless)
- **Connection Pooler (6543)**: Funziona su Vercel/serverless
- Il codice converte automaticamente 5432→6543, ma è meglio usare direttamente il pooler
- Neon è più semplice e affidabile per Vercel

## 🔗 Link Utili

- [Supabase Connection Pooling Docs](https://supabase.com/docs/guides/database/connecting-to-postgres#connection-pooler)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

---

**Ricorda**: Per Vercel/serverless, **sempre Connection Pooler (6543)**, mai Direct Connection (5432)!

