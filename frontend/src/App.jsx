import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useParams } from 'react-router-dom'
import { useEffect, useMemo, useState } from 'react'
import { toast, ToastContainer } from 'react-toastify'
import {
  Bell,
  Wallet,
  Home,
  User,
  History,
  LogOut,
  Menu,
  ChevronRight,
  CreditCard,
  ShieldCheck,
  TrendingUp,
  CircleDollarSign,
  ArrowUpRight,
  ArrowDownLeft,
} from 'lucide-react'
import api from './services/api'
import './App.css'
import 'react-toastify/dist/ReactToastify.css'

const betTypes = [
  'single_digit',
  'jodi_digit',
  'single_panna',
  'double_panna',
  'triple_panna',
  'half_sangam',
  'full_sangam',
]

const formatCurrency = (value) => `₹${Number(value || 0).toLocaleString('en-IN')}`

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }

    try {
      const { data } = await api.get('/api/auth/me')
      setUser(data.user)
    } catch {
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMe()
  }, [])

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    toast.success('Logged out successfully')
  }

  if (loading) return <div className="loading-screen">Loading...</div>

  return (
    <BrowserRouter>
      <div className="app-shell">
        <Routes>
          <Route path="/" element={user ? (user.role === 'admin' ? <Navigate to="/admin" replace /> : <Navigate to="/home" replace />) : <Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage onLogin={setUser} />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/home" element={user && user.role !== 'admin' ? <HomePage user={user} onRefresh={fetchMe} onLogout={logout} /> : <Navigate to="/login" replace />} />
          <Route path="/add-fund" element={user && user.role !== 'admin' ? <AddFundPage user={user} onRefresh={fetchMe} /> : <Navigate to="/login" replace />} />
          <Route path="/withdraw" element={user && user.role !== 'admin' ? <WithdrawPage user={user} onRefresh={fetchMe} /> : <Navigate to="/login" replace />} />
          <Route path="/bid-history" element={user && user.role !== 'admin' ? <BidHistoryPage /> : <Navigate to="/login" replace />} />
          <Route path="/transaction-history" element={user && user.role !== 'admin' ? <TransactionHistoryPage /> : <Navigate to="/login" replace />} />
          <Route path="/win-history" element={user && user.role !== 'admin' ? <WinHistoryPage /> : <Navigate to="/login" replace />} />
          <Route path="/game-rates" element={user && user.role !== 'admin' ? <GameRatesPage /> : <Navigate to="/login" replace />} />
          <Route path="/rules" element={user && user.role !== 'admin' ? <RulesPage /> : <Navigate to="/login" replace />} />
          <Route path="/change-password" element={user && user.role !== 'admin' ? <ChangePasswordPage /> : <Navigate to="/login" replace />} />
          <Route path="/game/:gameId" element={user && user.role !== 'admin' ? <GameTypePage /> : <Navigate to="/login" replace />} />
          <Route path="/game/:gameId/:betType" element={user && user.role !== 'admin' ? <BidPage /> : <Navigate to="/login" replace />} />

          <Route path="/admin" element={user && user.role === 'admin' ? <AdminDashboard /> : <Navigate to="/login" replace />} />
          <Route path="/admin/users" element={user && user.role === 'admin' ? <AdminUsersPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin/registrations" element={user && user.role === 'admin' ? <AdminRegistrationsPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin/games" element={user && user.role === 'admin' ? <AdminGamesPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin/bets" element={user && user.role === 'admin' ? <AdminBetsPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin/results" element={user && user.role === 'admin' ? <AdminResultsPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin/deposits" element={user && user.role === 'admin' ? <AdminDepositsPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin/withdrawals" element={user && user.role === 'admin' ? <AdminWithdrawalsPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin/transactions" element={user && user.role === 'admin' ? <AdminTransactionsPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin/settings" element={user && user.role === 'admin' ? <AdminSettingsPage /> : <Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <ToastContainer position="top-right" autoClose={2200} />
      </div>
    </BrowserRouter>
  )
}

function LoginPage({ onLogin }) {
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const { data } = await api.post('/api/auth/login', form)
      localStorage.setItem('token', data.token)
      onLogin(data.user)
      toast.success('Login successful')
      navigate(data.user.role === 'admin' ? '/admin' : '/home')
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Login failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Welcome</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="Username" />
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Password" />
          <button className="primary-btn" type="submit" disabled={submitting}>{submitting ? 'Please wait...' : 'Login'}</button>
        </form>
        <div className="auth-links">
          <Link to="/signup">Create account</Link>
        </div>
      </div>
    </div>
  )
}

function SignupPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', username: '', mobile: '', password: '', confirm_password: '' })
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 6) {
      toast.error('Password must be minimum 6 characters')
      return
    }
    if (form.password !== form.confirm_password) {
      toast.error('Passwords do not match')
      return
    }
    setSubmitting(true)
    try {
      await api.post('/api/auth/signup', form)
      toast.success('Registration submitted successfully. Please wait for admin approval.')
      navigate('/login')
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Signup failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Sign Up</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Name" />
          <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="Username" />
          <input value={form.mobile} onChange={(e) => setForm({ ...form, mobile: e.target.value })} placeholder="Mobile Number" />
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Password" />
          <input type="password" value={form.confirm_password} onChange={(e) => setForm({ ...form, confirm_password: e.target.value })} placeholder="Confirm Password" />
          <button className="primary-btn" type="submit" disabled={submitting}>{submitting ? 'Submitting...' : 'Sign Up'}</button>
        </form>
        <div className="auth-links">
          <Link to="/login">Already have an account?</Link>
        </div>
      </div>
    </div>
  )
}

function HomePage({ user, onRefresh, onLogout }) {
  const [games, setGames] = useState([])
  const [menuOpen, setMenuOpen] = useState(false)

  const loadGames = async () => {
    try {
      const { data } = await api.get('/api/games')
      setGames(data.games || [])
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Unable to load games')
    }
  }

  useEffect(() => { loadGames() }, [])

  const runningGames = games.filter((g) => g.is_running).sort((a, b) => a.sort_order - b.sort_order)
  const closedGames = games.filter((g) => !g.is_running).sort((a, b) => a.sort_order - b.sort_order)

  return (
    <div className="user-page">
      <header className="topbar">
        <button className="icon-btn" onClick={() => setMenuOpen(true)}><Menu size={22} /></button>
        <div className="brand">Website Name</div>
        <div className="wallet-pill"><Wallet size={18} /> {formatCurrency(user.wallet_balance)}</div>
      </header>

      {menuOpen && <div className="drawer-backdrop" onClick={() => setMenuOpen(false)} />}
      <aside className={`drawer ${menuOpen ? 'open' : ''}`}>
        <div className="drawer-header">
          <div className="avatar"><User size={18} /></div>
          <div>
            <strong>{user.name}</strong>
            <small>{user.mobile}</small>
            <small>{formatCurrency(user.wallet_balance)}</small>
          </div>
        </div>
        <nav className="drawer-nav">
          <Link to="/home" onClick={() => setMenuOpen(false)}><Home size={18} /> Home</Link>
          <Link to="/bid-history" onClick={() => setMenuOpen(false)}><History size={18} /> Bid History</Link>
          <Link to="/transaction-history" onClick={() => setMenuOpen(false)}><Wallet size={18} /> Transaction History</Link>
          <Link to="/win-history" onClick={() => setMenuOpen(false)}><TrendingUp size={18} /> Win History</Link>
          <Link to="/game-rates" onClick={() => setMenuOpen(false)}><CreditCard size={18} /> Game Rates</Link>
          <Link to="/rules" onClick={() => setMenuOpen(false)}><ShieldCheck size={18} /> Notice Board / Rules</Link>
          <Link to="/change-password" onClick={() => setMenuOpen(false)}><User size={18} /> Change Password</Link>
          <button className="logout-btn" onClick={() => { onLogout(); setMenuOpen(false) }}><LogOut size={18} /> Log Out</button>
        </nav>
      </aside>

      <div className="quick-actions">
        <Link to="/add-fund" className="action-btn">Add Fund</Link>
        <Link to="/withdraw" className="action-btn secondary">Withdraw</Link>
      </div>

      <div className="notice-bar">Announcement: Betting is open for all live games today.</div>

      <div className="games-list">
        {[...runningGames, ...closedGames].map((game) => (
          <div key={game.id} className="game-card">
            <h3>{game.name}</h3>
            <p className="game-status">{game.is_running ? 'Betting is Running' : 'Betting is Closed'}</p>
            <p className="game-time">Bet - {game.open_time} - {game.close_time}</p>
            <div className="game-footer">
              <span>{game.display_result || 'XXX-XX-XXX'}</span>
              {game.is_running ? (
                <Link to={`/game/${game.id}`} className="play-btn">Play Game</Link>
              ) : (
                <button className="play-btn disabled" disabled>Play Game</button>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="bottom-nav">
        <Link to="/home"><Home size={18} /> Home</Link>
        <Link to="/add-fund"><Wallet size={18} /> Fund</Link>
        <Link to="/bid-history"><History size={18} /> History</Link>
      </div>
    </div>
  )
}

function AddFundPage({ user, onRefresh }) {
  const navigate = useNavigate()
  const [amount, setAmount] = useState(100)
  const [method, setMethod] = useState('auto')
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    if (Number(amount) < 100) {
      toast.error('Minimum deposit is ₹100')
      return
    }
    setLoading(true)
    try {
      await api.post('/api/deposits', { amount, payment_method: method, transaction_reference: `DEP-${Date.now()}` })
      toast.success('Deposit request submitted successfully')
      onRefresh()
      navigate('/home')
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Deposit request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-shell">
      <div className="page-header">
        <Link to="/home" className="back-link">← Back</Link>
        <h2>Add Fund</h2>
      </div>
      <div className="panel">
        <div className="segmented">
          <button className={method === 'auto' ? 'active' : ''} onClick={() => setMethod('auto')}>Auto Recharge</button>
          <button className={method === 'manual' ? 'active' : ''} onClick={() => setMethod('manual')}>Manual Recharge</button>
        </div>
        <div className="amount-grid">
          {[100, 300, 500, 1000, 2000, 2500].map((value) => (
            <button key={value} className={Number(amount) === value ? 'amount-btn active' : 'amount-btn'} onClick={() => setAmount(value)}>{`₹${value}`}</button>
          ))}
        </div>
        <label>Enter Amount</label>
        <input type="number" value={amount} min="100" onChange={(e) => setAmount(e.target.value)} />
        <button className="primary-btn" onClick={submit} disabled={loading}>{loading ? 'Submitting...' : 'ADD FUNDS'}</button>
      </div>
    </div>
  )
}

function WithdrawPage({ user, onRefresh }) {
  const navigate = useNavigate()
  const [amount, setAmount] = useState(300)
  const [method, setMethod] = useState('bank')
  const [form, setForm] = useState({ account_holder_name: '', account_number: '', confirm_account_number: '', branch: '', ifsc: '', upi_id: '' })

  const submit = async () => {
    if (Number(amount) < 300) {
      toast.error('Minimum withdrawal is ₹300')
      return
    }
    if (Number(amount) > Number(user.wallet_balance || 0)) {
      toast.error('Cannot withdraw more than your balance')
      return
    }
    try {
      await api.post('/api/withdrawals', { ...form, amount, method })
      toast.success('Withdrawal request submitted successfully')
      onRefresh()
      navigate('/home')
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Withdrawal request failed')
    }
  }

  return (
    <div className="page-shell">
      <div className="page-header">
        <Link to="/home" className="back-link">← Back</Link>
        <h2>Withdraw</h2>
      </div>
      <div className="panel">
        <label>Amount</label>
        <input type="number" value={amount} min="300" onChange={(e) => setAmount(e.target.value)} />
        <div className="segmented">
          <button className={method === 'bank' ? 'active' : ''} onClick={() => setMethod('bank')}>Bank Account</button>
          <button className={method === 'upi' ? 'active' : ''} onClick={() => setMethod('upi')}>UPI</button>
        </div>

        {method === 'bank' ? (
          <div className="stacked-form">
            <input value={form.account_holder_name} onChange={(e) => setForm({ ...form, account_holder_name: e.target.value })} placeholder="Account Holder Name" />
            <input value={form.account_number} onChange={(e) => setForm({ ...form, account_number: e.target.value })} placeholder="Account Number" />
            <input value={form.confirm_account_number} onChange={(e) => setForm({ ...form, confirm_account_number: e.target.value })} placeholder="Confirm Account Number" />
            <input value={form.branch} onChange={(e) => setForm({ ...form, branch: e.target.value })} placeholder="Branch" />
            <input value={form.ifsc} onChange={(e) => setForm({ ...form, ifsc: e.target.value })} placeholder="IFSC" />
          </div>
        ) : (
          <div className="stacked-form">
            <input value={form.upi_id} onChange={(e) => setForm({ ...form, upi_id: e.target.value })} placeholder="UPI ID" />
          </div>
        )}

        <button className="primary-btn" onClick={submit}>Submit Request</button>
      </div>
    </div>
  )
}

function BidHistoryPage() {
  const [bids, setBids] = useState([])
  useEffect(() => {
    async function load() {
      const { data } = await api.get('/api/bids/history')
      setBids(data.bids || [])
    }
    load()
  }, [])

  return (
    <div className="page-shell">
      <div className="page-header"><Link to="/home" className="back-link">← Back</Link><h2>Bid History</h2></div>
      <div className="list-panel">
        {bids.map((bid) => (
          <div key={bid.id} className="record-row">
            <span>{bid.game}</span>
            <span>{bid.bid_type}</span>
            <span>{bid.bid_value}</span>
            <span>{formatCurrency(bid.amount)}</span>
            <span>{bid.result_status}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function TransactionHistoryPage() {
  const [items, setItems] = useState([])
  useEffect(() => {
    async function load() {
      const { data } = await api.get('/api/transactions')
      setItems(data.transactions || [])
    }
    load()
  }, [])

  return (
    <div className="page-shell">
      <div className="page-header"><Link to="/home" className="back-link">← Back</Link><h2>Transaction History</h2></div>
      <div className="list-panel">
        {items.map((tx) => (
          <div key={tx.id} className="record-row">
            <span>{tx.type}</span>
            <span>{formatCurrency(tx.amount)}</span>
            <span>{tx.status}</span>
            <span>{tx.description}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function WinHistoryPage() {
  const [wins, setWins] = useState([])
  useEffect(() => {
    async function load() {
      const { data } = await api.get('/api/wins')
      setWins(data.wins || [])
    }
    load()
  }, [])

  return (
    <div className="page-shell">
      <div className="page-header"><Link to="/home" className="back-link">← Back</Link><h2>Win History</h2></div>
      <div className="list-panel">
        {wins.map((win) => (
          <div key={win.id} className="record-row">
            <span>{win.game}</span>
            <span>{win.bid_type}</span>
            <span>{win.bid_value}</span>
            <span>{formatCurrency(win.win_amount)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function GameRatesPage() {
  return (
    <div className="page-shell">
      <div className="page-header"><Link to="/home" className="back-link">← Back</Link><h2>Game Rates</h2></div>
      <div className="panel rates-panel">
        <ul>
          <li>Single Digit = 9x</li>
          <li>Jodi Digit = 90x</li>
          <li>Single Panna = 140x</li>
          <li>Double Panna = 280x</li>
          <li>Triple Panna = 900x</li>
          <li>Half Sangam = 1200x</li>
          <li>Full Sangam = 10000x</li>
        </ul>
      </div>
    </div>
  )
}

function RulesPage() {
  return (
    <div className="page-shell">
      <div className="page-header"><Link to="/home" className="back-link">← Back</Link><h2>Rules</h2></div>
      <div className="panel">
        <ul className="rules-list">
          <li>Only approved users can place bets.</li>
          <li>Minimum deposit is ₹100.</li>
          <li>Minimum withdrawal is ₹300.</li>
          <li>Only running games accept bets.</li>
          <li>All winning calculations are processed on the backend.</li>
        </ul>
      </div>
    </div>
  )
}

function ChangePasswordPage() {
  return (
    <div className="page-shell">
      <div className="page-header"><Link to="/home" className="back-link">← Back</Link><h2>Change Password</h2></div>
      <div className="panel">
        <input placeholder="Current Password" type="password" />
        <input placeholder="New Password" type="password" />
        <input placeholder="Confirm New Password" type="password" />
        <button className="primary-btn">Update Password</button>
      </div>
    </div>
  )
}

function GameTypePage() {
  const { gameId } = useParams()
  const [game, setGame] = useState(null)
  useEffect(() => {
    async function load() {
      const { data } = await api.get(`/api/games/${gameId}`)
      setGame(data.game)
    }
    load()
  }, [gameId])

  const typeLabels = {
    single_digit: 'Single Digit',
    jodi_digit: 'Jodi Digit',
    single_panna: 'Single Panna',
    double_panna: 'Double Panna',
    triple_panna: 'Triple Panna',
    half_sangam: 'Half Sangam',
    full_sangam: 'Full Sangam',
  }

  return (
    <div className="page-shell">
      <div className="page-header"><Link to="/home" className="back-link">← Back</Link><h2>{game?.name || 'Game'}</h2></div>
      <div className="type-grid">
        {Object.entries(typeLabels).map(([key, label]) => (
          <Link key={key} to={`/game/${gameId}/${key}`} className="type-card">{label}</Link>
        ))}
      </div>
    </div>
  )
}

function BidPage() {
  const { gameId, betType } = useParams()
  const navigate = useNavigate()
  const [game, setGame] = useState(null)
  const [selectedValue, setSelectedValue] = useState('')
  const [amount, setAmount] = useState(10)
  const [summary, setSummary] = useState([])
  const [total, setTotal] = useState(0)

  const getBetLabel = () => {
    const labels = {
      single_digit: 'Single Digit',
      jodi_digit: 'Jodi Digit',
      single_panna: 'Single Panna',
      double_panna: 'Double Panna',
      triple_panna: 'Triple Panna',
      half_sangam: 'Half Sangam',
      full_sangam: 'Full Sangam',
    }
    return labels[betType] || 'Bet'
  }

  useEffect(() => {
    async function loadGame() {
      const { data } = await api.get(`/api/games/${gameId}`)
      setGame(data.game)
    }
    loadGame()
  }, [gameId])

  const digitOptions = betType === 'jodi_digit'
    ? Array.from({ length: 100 }, (_, index) => String(index).padStart(2, '0'))
    : ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
  const isPanna = ['single_panna', 'double_panna', 'triple_panna'].includes(betType)
  const pannaPlaceholder = {
    single_panna: 'Enter 3 different digits',
    double_panna: 'Enter AAB or ABB digits',
    triple_panna: 'Enter 3 same digits',
  }

  const addBid = () => {
    const validValue = betType === 'jodi_digit'
      ? /^\d{2}$/.test(selectedValue)
      : betType === 'single_panna'
        ? /^\d{3}$/.test(selectedValue) && new Set(selectedValue).size === 3
        : betType === 'double_panna'
          ? /^\d{3}$/.test(selectedValue) && (selectedValue[0] === selectedValue[1] || selectedValue[1] === selectedValue[2]) && selectedValue[0] !== selectedValue[2]
          : betType === 'triple_panna'
            ? /^\d{3}$/.test(selectedValue) && new Set(selectedValue).size === 1
        : selectedValue.length > 0
    if (!validValue || Number(amount) < 10) {
      toast.error('Please enter a valid bid value and amount')
      return
    }
    const next = [...summary, { bid_value: selectedValue, amount: Number(amount) }]
    setSummary(next)
    setTotal(next.reduce((sum, item) => sum + Number(item.amount), 0))
    setSelectedValue('')
    setAmount(10)
  }

  const placeBid = async () => {
    if (!summary.length) {
      toast.error('Add at least one bid before placing')
      return
    }
    try {
      for (const item of summary) {
        await api.post('/api/bids', {
          game_id: Number(gameId),
          bid_type: betType,
          bid_value: item.bid_value,
          amount: item.amount,
        })
      }
      toast.success('Your bid is placed successfully.')
      navigate('/home')
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Unable to place bid')
    }
  }

  return (
    <div className="page-shell">
      <div className="page-header"><Link to={`/game/${gameId}`} className="back-link">← Back</Link><h2>{game?.name || 'Game'}</h2></div>
      <div className="panel">
        <h3>{getBetLabel()}</h3>
        {!isPanna && <div className={`digit-grid ${betType === 'jodi_digit' ? 'jodi-grid' : ''}`}>
          {digitOptions.map((digit) => (
            <button key={digit} className={selectedValue === digit ? 'digit-btn active' : 'digit-btn'} onClick={() => setSelectedValue(digit)}>{digit}</button>
          ))}
        </div>}
        <label>Number</label>
        <input
          value={selectedValue}
          maxLength={betType === 'jodi_digit' ? 2 : isPanna ? 3 : undefined}
          inputMode="numeric"
          onChange={(e) => setSelectedValue(e.target.value.replace(/\D/g, '').slice(0, betType === 'jodi_digit' ? 2 : isPanna ? 3 : undefined))}
          placeholder={betType === 'jodi_digit' ? 'Enter 00-99' : pannaPlaceholder[betType] || 'Enter value'}
        />
        <label>Amount</label>
        <input type="number" min="10" value={amount} onChange={(e) => setAmount(e.target.value)} />
        <button className="primary-btn" onClick={addBid}>Add Bid</button>

        <div className="summary-box">
          <h4>Bid Summary</h4>
          {summary.length ? summary.map((item, idx) => (
            <div className="summary-item" key={`${item.bid_value}-${idx}`}>{`Number: ${item.bid_value}  ₹${item.amount}`}</div>
          )) : <div>No bids yet</div>}
          <div className="summary-total">Total Amount: {formatCurrency(total)}</div>
        </div>

        <button className="primary-btn" onClick={placeBid}>Place Bid</button>
      </div>
    </div>
  )
}

function AdminDashboard() {
  const [stats, setStats] = useState({ users: 0, total_wallet: 0, pending_bets: 0, payment_queue: 0, withdrawal_queue: 0 })
  useEffect(() => {
    async function load() {
      const { data } = await api.get('/api/admin/dashboard')
      setStats(data.stats)
    }
    load()
  }, [])

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <h2>Admin</h2>
        <nav>
          <Link to="/admin">Dashboard</Link>
          <Link to="/admin/users">Manage Users</Link>
          <Link to="/admin/registrations">Registration Requests</Link>
          <Link to="/admin/results">Manage Result</Link>
          <Link to="/admin/bets">Manage Bets</Link>
          <Link to="/admin/games">Manage Games</Link>
          <Link to="/admin/transactions">All Transactions</Link>
          <Link to="/admin/deposits">Deposit Requests</Link>
          <Link to="/admin/withdrawals">Withdrawal Queue</Link>
          <Link to="/admin/settings">Settings</Link>
        </nav>
      </aside>
      <main className="admin-main">
        <div className="stats-grid">
          <div className="stat-card"><span>Total Users</span><strong>{stats.users}</strong></div>
          <div className="stat-card"><span>Total Wallet</span><strong>{formatCurrency(stats.total_wallet)}</strong></div>
          <div className="stat-card"><span>Pending Bet</span><strong>{stats.pending_bets}</strong></div>
          <div className="stat-card"><span>Payment Queue</span><strong>{stats.payment_queue}</strong></div>
          <div className="stat-card"><span>Withdrawal Queue</span><strong>{stats.withdrawal_queue}</strong></div>
        </div>
      </main>
    </div>
  )
}

function AdminUsersPage() {
  const [users, setUsers] = useState([])
  const load = async () => {
    const { data } = await api.get('/api/admin/users')
    setUsers(data.users || [])
  }

  useEffect(() => { load() }, [])

  const updateStatus = async (userId, status) => {
    await api.patch(`/api/admin/users/${userId}`, { status })
    load()
  }

  return (
    <AdminLayout>
      <h2>Manage Users</h2>
      <table>
        <thead><tr><th>Username</th><th>Phone</th><th>Fund</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}><td>{user.username}</td><td>{user.mobile}</td><td>{formatCurrency(user.wallet_balance)}</td><td>{user.status}</td><td><button onClick={() => updateStatus(user.id, 'approved')}>Approve</button><button onClick={() => updateStatus(user.id, 'blocked')}>Block</button></td></tr>
          ))}
        </tbody>
      </table>
    </AdminLayout>
  )
}

function AdminRegistrationsPage() {
  const [users, setUsers] = useState([])
  const load = async () => {
    const { data } = await api.get('/api/admin/registrations')
    setUsers(data.users || [])
  }

  useEffect(() => { load() }, [])

  const act = async (id, action) => {
    await api.patch(`/api/admin/registrations/${id}`, { action })
    load()
  }

  return (
    <AdminLayout>
      <h2>Registration Requests</h2>
      <div className="list-panel">
        {users.map((user) => (
          <div className="record-row" key={user.id}><span>{user.name}</span><span>{user.username}</span><span>{user.mobile}</span><span>{user.status}</span><span><button onClick={() => act(user.id, 'approve')}>Approve</button><button onClick={() => act(user.id, 'reject')}>Reject</button></span></div>
        ))}
      </div>
    </AdminLayout>
  )
}

function AdminGamesPage() {
  const [games, setGames] = useState([])
  const load = async () => {
    const { data } = await api.get('/api/admin/games')
    setGames(data.games || [])
  }

  useEffect(() => { load() }, [])

  const updateGame = async (gameId, payload) => {
    await api.put(`/api/admin/games/${gameId}`, payload)
    load()
  }

  return (
    <AdminLayout>
      <h2>Manage Games</h2>
      <div className="list-panel">
        {games.map((game) => (
          <div className="record-row admin-game-row" key={game.id}>
            <span>{game.name}</span>
            <select value={game.is_running ? 'running' : 'closed'} onChange={(e) => updateGame(game.id, { is_running: e.target.value === 'running' })}><option value="running">Running</option><option value="closed">Closed</option></select>
            <input value={game.open_time} onChange={(e) => updateGame(game.id, { open_time: e.target.value })} />
            <input value={game.close_time} onChange={(e) => updateGame(game.id, { close_time: e.target.value })} />
          </div>
        ))}
      </div>
    </AdminLayout>
  )
}

function AdminBetsPage() {
  const [bets, setBets] = useState([])
  useEffect(() => {
    async function load() {
      const { data } = await api.get('/api/admin/bets')
      setBets(data.bets || [])
    }
    load()
  }, [])

  return (
    <AdminLayout>
      <h2>Manage Bets</h2>
      <div className="list-panel scroll-list">
        {bets.map((bet) => (
          <div key={bet.id} className="record-row">
            <span>{bet.user}</span>
            <span>{bet.game}</span>
            <span>{bet.bid_type}</span>
            <span>{bet.bid_value}</span>
            <span>{formatCurrency(bet.amount)}</span>
            <span>{bet.status}</span>
          </div>
        ))}
      </div>
    </AdminLayout>
  )
}

function AdminResultsPage() {
  const [results, setResults] = useState([])
  const [drafts, setDrafts] = useState({})
  const [submitting, setSubmitting] = useState(null)
  const load = async () => {
    const { data } = await api.get('/api/admin/results')
    const nextResults = data.results || []
    setResults(nextResults)
    setDrafts(Object.fromEntries(nextResults.map((row) => [row.game_id, {
      single_digit: row.result?.single_digit || '',
      jodi_digit: row.result?.jodi_digit || '',
    }])))
  }

  useEffect(() => { load() }, [])

  const updateDraft = (gameId, field, value) => {
    setDrafts((current) => ({ ...current, [gameId]: { ...current[gameId], [field]: value } }))
  }

  const submit = async (gameId) => {
    setSubmitting(gameId)
    try {
      await api.post('/api/admin/results', { game_id: gameId, ...drafts[gameId] })
      toast.success('Result published successfully')
      await load()
    } catch (err) {
      toast.error(err?.response?.data?.error || 'Result submission failed')
    } finally {
      setSubmitting(null)
    }
  }

  return (
    <AdminLayout>
      <h2>Manage Result</h2>
      <div className="list-panel">
        {results.map((row) => (
          <div className="record-row result-row" key={row.game_id}>
            <span>{row.game_name}</span>
            <input value={drafts[row.game_id]?.single_digit || ''} maxLength="1" inputMode="numeric" placeholder="Single digit" onChange={(e) => updateDraft(row.game_id, 'single_digit', e.target.value)} />
            <input value={drafts[row.game_id]?.jodi_digit || ''} maxLength="2" inputMode="numeric" placeholder="Jodi digit" onChange={(e) => updateDraft(row.game_id, 'jodi_digit', e.target.value)} />
            <button className="primary-btn" onClick={() => submit(row.game_id)} disabled={submitting === row.game_id}>{submitting === row.game_id ? 'Submitting...' : 'Submit'}</button>
          </div>
        ))}
      </div>
    </AdminLayout>
  )
}

function AdminDepositsPage() {
  const [items, setItems] = useState([])
  const load = async () => {
    const { data } = await api.get('/api/admin/deposits')
    setItems(data.deposits || [])
  }
  useEffect(() => { load() }, [])
  const update = async (id, action) => {
    await api.patch(`/api/admin/deposits/${id}`, { action })
    load()
  }
  return <AdminLayout><h2>Deposit Requests</h2><div className="list-panel">{items.map((item) => <div className="record-row" key={item.id}><span>{item.user}</span><span>{formatCurrency(item.amount)}</span><span>{item.status}</span><span><button onClick={() => update(item.id, 'approve')}>Approve</button><button onClick={() => update(item.id, 'reject')}>Reject</button></span></div>)}</div></AdminLayout>
}

function AdminWithdrawalsPage() {
  const [items, setItems] = useState([])
  const load = async () => { const { data } = await api.get('/api/admin/withdrawals'); setItems(data.withdrawals || []) }
  useEffect(() => { load() }, [])
  const update = async (id, action) => { await api.patch(`/api/admin/withdrawals/${id}`, { action }); load() }
  return <AdminLayout><h2>Withdrawal Queue</h2><div className="list-panel">{items.map((item) => <div className="record-row" key={item.id}><span>{item.user}</span><span>{formatCurrency(item.amount)}</span><span>{item.status}</span><span><button onClick={() => update(item.id, 'process')}>Process</button><button onClick={() => update(item.id, 'success')}>Success</button><button onClick={() => update(item.id, 'reject')}>Reject</button></span></div>)}</div></AdminLayout>
}

function AdminTransactionsPage() {
  const [items, setItems] = useState([])
  useEffect(() => { api.get('/api/admin/transactions').then(({ data }) => setItems(data.transactions || [])) }, [])
  return <AdminLayout><h2>All Transactions</h2><div className="list-panel">{items.map((item) => <div className="record-row" key={item.id}><span>{item.user}</span><span>{item.type}</span><span>{formatCurrency(item.amount)}</span><span>{item.status}</span></div>)}</div></AdminLayout>
}

function AdminSettingsPage() {
  return <AdminLayout><h2>Settings</h2><div className="panel"><p>Compliance, age check, and platform settings can be adjusted here.</p></div></AdminLayout>
}

function AdminLayout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <div className="admin-shell">
      <div className="admin-mobile-bar">
        <strong>Admin Panel</strong>
        <button className="icon-btn" onClick={() => setMenuOpen((open) => !open)} aria-label="Toggle admin navigation">
          <Menu size={22} />
        </button>
      </div>
      {menuOpen && <div className="admin-menu-overlay" onClick={() => setMenuOpen(false)} />}
      <aside className={`admin-sidebar ${menuOpen ? 'open' : ''}`}>
        <h2>Admin</h2>
        <nav>
          <Link to="/admin" onClick={() => setMenuOpen(false)}>Dashboard</Link>
          <Link to="/admin/users" onClick={() => setMenuOpen(false)}>Manage Users</Link>
          <Link to="/admin/registrations" onClick={() => setMenuOpen(false)}>Registration Requests</Link>
          <Link to="/admin/results" onClick={() => setMenuOpen(false)}>Manage Result</Link>
          <Link to="/admin/bets" onClick={() => setMenuOpen(false)}>Manage Bets</Link>
          <Link to="/admin/games" onClick={() => setMenuOpen(false)}>Manage Games</Link>
          <Link to="/admin/transactions" onClick={() => setMenuOpen(false)}>All Transactions</Link>
          <Link to="/admin/deposits" onClick={() => setMenuOpen(false)}>Deposit Requests</Link>
          <Link to="/admin/withdrawals" onClick={() => setMenuOpen(false)}>Withdrawal Queue</Link>
          <Link to="/admin/settings" onClick={() => setMenuOpen(false)}>Settings</Link>
        </nav>
      </aside>
      <main className="admin-main">{children}</main>
    </div>
  )
}

export default App
