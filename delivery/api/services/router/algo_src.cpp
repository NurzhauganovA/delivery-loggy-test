#pragma comment(linker, "/stack:20000000")
#pragma GCC optimize("Ofast")
//#pragma GCC target("sse,sse2,sse3,ssse3,sse4,popcnt,abm,mmx")
#include <bits/stdc++.h> 
using namespace std;
#define f first
#define s second
#define pb push_back
#define mp make_pair
#define forit(v,it) for(typeof(v.begin()) it = v.begin(); it != v.end(); ++it)
typedef vector <int> vi;
typedef pair <int,int> pii;
typedef long long ll;
typedef long double ld;
typedef vector <vi> vvi;
typedef pair <double, int> pdi;
typedef pair <int, double> pid;
typedef pair <double, double> pdd;


const int maxn = 311, inf = (1 << 26), k_ext = 2, max_it_local_search = 50, Max_it = 100, cnt_iter = 1, max_courier = 42; 
const double tau_min = 0.001, tau_max = 0.999, q_0 = 0.9, p_0 = 0.45, eps = 1e-6, _beta = 2.0;
int c_num, k_bw, n, Time[max_courier][maxn][maxn], dist[maxn][maxn], c_len, c_ind, Dist_lim, fin_time, t_arr[maxn];
double tau[maxn][maxn], nu[maxn][maxn], tau_delta[maxn][maxn];
int time_l_min, time_r_min, time_l_max, time_r_max, dist_min, dist_max, ans_path[maxn], A[maxn];
bool used[maxn], used2[maxn], used_v[maxn], calced[maxn], is_can[maxn][maxn];
int prev_ind[maxn], next_ind[maxn], cm, comp[maxn], cnt_comp[maxn], num_comp_st[maxn], num_comp[maxn], cur_cnt_comp[maxn];
int dist_to_depot[maxn], is_cycle;
pair <pii, int> Courier_ans;
vi lv[maxn];
pair <pdi, pii> pd[max_courier * maxn], vd[max_courier * maxn];
pid glob_viol;


struct Order {
	int time_ready, deadline, priority, service_time;
	Order() {
	}
	Order(int _time_ready, int _deadline, int _priority, int _service_time) {
		time_ready = _time_ready, deadline = _deadline;
		priority = _priority, service_time = _service_time;
	}
} ord[maxn];

struct Courier {
	double speed;
	int dist_limit, viol, dist, Time, start_time, finish_time;
	Courier() {
		viol = dist = Time = 0;
	}
	Courier(double _sp, int _dist_l, int _viol, int _dist, int _Time, int _start_time, int _finish_time) {
		speed = _sp, dist_limit = _dist_l;
		viol = _viol, dist = _dist, Time = _Time;
		start_time = _start_time, finish_time = _finish_time;
	}
	bool operator < (Courier C) const {
		return (mp(viol, dist) < mp(C.viol, C.dist));
	}
} Cr[maxn];

typedef pair <vvi, vector <Courier> > pc;
typedef vector <pc> vpc;
pc glob_path;


void add_back_depot_dist(vvi &v, vector <Courier> &vc) { //Complexity: O(c_num)
	for(int k = 0;k < c_num;++k) if(v[k].size() > 1) {
		int j = v[k].back();
		assert(j != 0);
		v[k].pb(0);
		vc[k].dist += dist[j][0];
		int cur_time = max(vc[k].Time + Time[k][j][0], ord[0].time_ready);
		if(cur_time > ord[0].deadline) vc[k].viol += ord[0].priority;
		vc[k].Time = cur_time;

		assert(vc[k].dist <= vc[k].dist_limit);
		assert(cur_time <= vc[k].finish_time);
	}
}


pid violate(vector <Courier> &vc) {//���������� ������� � ��� �����. Complexity: O(c_num)
	if(vc.size() != c_num) return mp(inf, inf);
	double max_dist = 0;
	int total_viol = 0;
	for(int i = 0;i < c_num;++i) {
		max_dist = max(max_dist, vc[i].dist / vc[i].speed);
		total_viol += vc[i].viol;
		if(total_viol > inf) total_viol = inf;
	}

	return mp(total_viol, max_dist);
}

Courier violate2(vi &v, Courier &C, int K) { //Complexity: O(v.size())
	Courier res = C;
	assert(!v.empty());
	if(v.size() == 2  &&  v.back() == 0) {
		res.viol = res.dist = res.Time = 0;
		return res;
	}

	int cur_time = C.start_time, sum_dist = 0, cur_viol = 0, len = v.size();
	forit(v, it)
		used_v[*it] = 0;

	int from, to = v[0];
	used_v[to] = true;
	bool ok = true;
	for(int i = 1;i < len;++i) {
		from = v[i - 1], to = v[i];
		if(!is_can[K][from]) {
			ok = false;
			break;
		}
		int num = prev_ind[to];
		if(num != -1  &&  !used_v[num]) {
			ok = false;
			break;
		}
		cur_time = max(cur_time + Time[K][from][to], ord[to].time_ready);
		if(cur_time > C.finish_time) {
			ok = false;
			break;
		}
		if(cur_time > ord[to].deadline) cur_viol += ord[to].priority;
		sum_dist += dist[from][to];

		if(sum_dist > C.dist_limit) {
			ok = false;
			break;
		}
		used_v[to] = true;
      }
      if(!ok) res.viol = res.dist = res.Time = inf;
      else res.viol = cur_viol, res.dist = sum_dist, res.Time = cur_time;
      return res;
}

pair <int, pii> select_det(pair <pdi, pii> *C, int len) { //select_deterministically. Complexity: O(len)
	pair <pdi, pii> Max = C[0];
	for(int i = 1;i < len;++i) if(Max < C[i])
		Max = C[i];

	return mp(Max.f.s, Max.s);
}

pair <int, pii> select_prob(pair <pdi, pii> *C, int len) { //select probabilistically. Complexity: O(len)
	assert(len > 0);
	double qq = 1.0 * rand() / 32767, sum = 0;
	for(int i = 0;i < len;++i)
		sum += C[i].f.f;

	qq *= sum;
	double cur_sum = 0;
	for(int i = 0;i < len;++i) {
		cur_sum += C[i].f.f;
		if(cur_sum + eps > qq) return mp(C[i].f.s, C[i].s);
	}
	return mp(C[len - 1].f.s, C[len - 1].s);
}

pair <int, pii> choose_from(pair <pdi, pii> *C, int len) {  //Complexity: O(len)
	assert(len > 0);
	double qq = 1.0 * rand() / 32767;
	if(qq <= q_0) return select_det(C, len);
	return select_prob(C, len);
}


pid calc_expected_value(vvi v, vector <Courier> vc) {   //Complexity: O(n^2 * c_num)
	memset(used2, 0, sizeof(used2));
	memset(num_comp_st, -1, sizeof(num_comp_st));
	int cur_size = 0, cnum_it = 0;

	forit(v, it) {
		vi V = *it;
		forit(V, it2) {
			used2[*it2] = true;
			if(*it2 > 0) cur_size++;
			int n_comp = comp[*it2];
			if(n_comp != 0) num_comp_st[n_comp] = cnum_it;
		}
		cnum_it++;
	}
	          
	while(cur_size < n) {
		int pdn = 0;
		for(int j = 1;j <= n;++j) if(!used2[j]) {
			int num = prev_ind[j];
			if(num != -1  &&  !used2[num]) continue;
			int ind_comp = comp[j];

			for(int k = 0;k < c_num;++k) if(is_can[k][j]) {
				int i = v[k].back();
			      if(ind_comp != 0  &&  num_comp_st[ind_comp] != -1  &&  num_comp_st[ind_comp] != k) continue;

				if(vc[k].dist + dist[i][j] + dist_to_depot[j] > vc[k].dist_limit) continue;

				int cur_time = vc[k].Time, from = i, to = j;
				while(true) {
					cur_time = max(cur_time + Time[k][from][to], ord[to].time_ready);
					if(to == 0) break;
					from = to;
					to = next_ind[to];
					if(to == -1) to = 0;
				}

				if(cur_time <= vc[k].finish_time)
					pd[pdn++] = mp(mp(tau[i][j] * nu[i][j], k), mp(i, j));
			}
		}
		if(pdn == 0) return mp(inf, inf);

		pair <int, pii> P = choose_from(pd, pdn);
		int from = P.s.f, to = P.s.s, ind = P.f;
		used2[to] = true;
		cur_size++;
		if(comp[to] != 0) num_comp_st[comp[to]] = ind;
		assert(ind != -1);

		v[ind].pb(to);
		int cur_time = max(vc[ind].Time + Time[ind][from][to], ord[to].time_ready);
		vc[ind].Time = cur_time;
		if(cur_time > ord[to].deadline) vc[ind].viol += ord[to].priority;
		vc[ind].dist += dist[from][to];
	}
	     
	add_back_depot_dist(v, vc);

	pid cur = violate(vc);
	if(cur < glob_viol) 
		glob_viol = cur, glob_path = mp(v, vc);

	return cur;
}


void update(vpc &A) { //Complexity: O(k_bw * k_ext * n^2 * c_num)
	set <pair <pid, pc> > S;
	S.clear();   
	forit(A, it) {
		vvi V = (*it).f;
		vector <Courier> vc = (*it).s;

		memset(used, 0, sizeof(used));
		memset(num_comp, -1, sizeof(num_comp));
		int cnum_it = 0;
		forit(V, it2) {
			vi v = *it2;
			forit(v, it3) {
				used[*it3] = true;
				int n_comp = comp[*it3];
				if(n_comp != 0) num_comp[n_comp] = cnum_it;
			}
			cnum_it++;
		}

		int vdn = 0;
		
		for(int j = 1;j <= n;++j) if(!used[j]) {
		      int num = prev_ind[j];
			if(num != -1  &&  !used[num]) continue;
			int ind_comp = comp[j];

			for(int k = 0;k < c_num;++k) if(is_can[k][j]) {
				int i = V[k].back();
			     if(ind_comp != 0  &&  num_comp[ind_comp] != -1  &&  num_comp[ind_comp] != k) continue;

			      if(vc[k].dist + dist[i][j] + dist_to_depot[j] > vc[k].dist_limit) continue;

			      int cur_time = vc[k].Time, from = i, to = j;
				while(true) {
					cur_time = max(cur_time + Time[k][from][to], ord[to].time_ready);
					if(to == 0) break;
					from = to;
					to = next_ind[to];
					if(to == -1) to = 0;
				}

				if(cur_time <= vc[k].finish_time)
					vd[vdn++] = mp(mp(tau[i][j] * nu[i][j], k), mp(i, j));
			} 
		}

		if(vdn == 0) continue;

		set <pair <pid, pc> > St;
		St.clear();

		for(int it2 = 0;it2 < k_ext;++it2) {
			pair <int, pii> P = select_prob(vd, vdn);
			int from = P.s.f, to = P.s.s, ind = P.f;

			assert(ind != -1);
			V[ind].pb(to);
			Courier cur_courier = vc[ind];
			int cur_time = max(vc[ind].Time + Time[ind][from][to], ord[to].time_ready);
			if(cur_time > ord[to].deadline) vc[ind].viol += ord[to].priority;
			vc[ind].dist += dist[from][to];
			vc[ind].Time = cur_time;
		
			pid P2 = calc_expected_value(V, vc);
			St.insert(mp(P2, mp(V, vc)));
			if(St.size() > k_ext) {
				set <pair <pid, pc> >::iterator It = --St.end();
				St.erase(It);
			}

			V[ind].pop_back();
			vc[ind] = cur_courier;
		}
		forit(St, It) {
			S.insert(*It);
			if(S.size() > k_bw) {
				set <pair <pid, pc> >::iterator It2 = --S.end();
				S.erase(It2);
			}
		}
	}  
	
	A.clear();
	forit(S, It)
		A.pb((*It).s);
}


void calc_nu() { //Complexity: O(n^2)
	for(int i = 0;i <= n;++i) {
		for(int j = 0;j <= n;++j) if(i != j) 
			nu[i][j] = 100.0 / max(1, dist[i][j]);
		
	}
} 

pc min_viol(vpc &V) { //Complexity: O(k_bw * n)
	pid Min = glob_viol;
	pc res = glob_path;
      forit(V, it) {
      	vvi v = (*it).f;
      	vector <Courier> vc = (*it).s;
      	add_back_depot_dist(v, vc);
		pid cur = violate(vc);
		if(Min > cur) {
			Min = cur;
			res = mp(v, vc);
		}
	} 
	
	return res;
}

pc pbs() { //probabilistic beam search. Complexity: O(k_bw * k_ext * n^3 * c_num)
	vector <Courier> vc;

	vpc B0;
	vi V;
	V.pb(0);
	vvi VV;
	for(int i = 0;i < c_num;++i) {
		VV.pb(V);
		vc.pb(Cr[i]);
	}
	B0.pb(mp(VV, vc));
	glob_viol = mp(inf, inf);

	for(int t = 0;t < n;++t)  
		update(B0);
	
	return min_viol(B0);
}

void init_tau() { //Complexity: O(n^2)
	for(int i = 0;i <= n;++i)
      	for(int j = i + 1;j <= n;++j)
      		tau[i][j] = tau[j][i] = tau_max;
}

double compute_conv_factor() { //compute convengence factor. Complexity: O(n^2)
	double sum = 0;
	for(int i = 0;i <= n;++i)
		for(int j = 0;j <= n;++j) if(i != j) 
			sum += max(tau_max - tau[i][j], tau[i][j] - tau_min);
	
	double T = (n + 1.0) * (n + 1.0);
	double res = 2 * sum / (T * (tau_max - tau_min)) - 1; 
	return res;     
}

void calc_coef(double &k_ib, double &k_rb, double &k_bf, double cf, bool bs_update) { //Complexity: O(1)
	if(bs_update) {
		k_ib = k_rb = 0, k_bf = 1;
		return;
	}
	if(cf < 0.4) {
		k_ib = 1, k_rb = k_bf = 0;
	}
	else if(cf < 0.6) {
		k_ib = 2.0 / 3, k_rb = 1.0 / 3, k_bf = 0;
	}
	else if(cf < 0.8) {
		k_ib = 1.0 / 3, k_rb = 2.0 / 3, k_bf = 0;
	}
	else {
		k_ib = k_bf = 0, k_rb = 1;
	}
}

void add_pheromone(vvi &V, double k) { //Complexity: O(n)
	forit(V, it) {
		vi v = *it;
	//	if(v.back() != 0) v.pb(0);
		int len = v.size() - 1;
		for(int i = 0;i < len;++i)
			tau_delta[v[i]][v[i + 1]] += k;
	}          
}


void pheromone_update(double cf, bool bs_update, vvi &p_ib, vvi &p_rb, vvi &p_bf) { //Complexity: O(n^2)
	double k_ib, k_rb, k_bf;
	calc_coef(k_ib, k_rb, k_bf, cf, bs_update);
	for(int i = 0;i <= n;++i)
		for(int j = i + 1;j <= n;++j)
			tau_delta[i][j] = tau_delta[j][i] = 0;
	
	add_pheromone(p_ib, k_ib);
	add_pheromone(p_rb, k_rb);
	add_pheromone(p_bf, k_bf);
	
	for(int i = 0;i <= n;++i)
		for(int j = 0;j <= n;++j) if(i != j) {
			tau[i][j] = tau[i][j] + p_0 * (tau_delta[i][j] - tau[i][j]);
			if(tau[i][j] > tau_max + eps) tau[i][j] = tau_max;
			if(tau[i][j] + eps < tau_min) tau[i][j] = tau_min;
		} 
}
            

void local_search_1_opt(pc &V, int K, bool &change) { //Max Complexity: O(N^3), where N = v.size()
//	assert(v == V.f[K]);
	vi p_best = V.f[K];
	vi v = p_best;
	Courier Best = V.s[K];
	int N = V.f[K].size() - 2;
	for(int k = 1;k < N;++k) if(prev_ind[v[k + 1]] != v[k]) {
		vi v2 = v;
		std::iter_swap(v2.begin() + k, v2.begin() + k + 1);
		Courier C = violate2(v2, V.s[K], K);
		if(C < Best)
			p_best = v2, Best = C, change = true;

		vi v3 = v2;
		for(int d = k + 1;d < N;++d) {
			if(prev_ind[v2[d + 1]] == v2[d]) break;
			std::iter_swap(v2.begin() + d, v2.begin() + d + 1);
			C = violate2(v2, V.s[K], K);
			if(C < Best)
				p_best = v2, Best = C, change = true;
		}
		v2 = v3;

		for(int d = k - 1;d > 0;--d) {
			if(prev_ind[v2[d + 1]] == v2[d]) break;
			std::iter_swap(v2.begin() + d, v2.begin() + d + 1);
			C = violate2(v2, V.s[K], K);
			if(C < Best)
				p_best = v2, Best = C, change = true;
		}
	}
	V.f[K] = p_best;
	V.s[K] = Best;
}

void local_search_2_opt(pc &V, int K) { //Max Complexity: O(N^3 * max_it_local_search), where N = v.size()
//	assert(v == V.f[K]);
	Courier Best = V.s[K];
	int N = V.f[K].size() - 2;
	vi v = V.f[K];

	for(int iter = 0;iter < max_it_local_search;++iter) {
		vi p_rb;
		Courier cur_best = Best;
		int max_prev_ind = 0;
		for(int j = 2;j <= N;++j) {
			int cur_v = v[j];
			int Num = prev_ind[cur_v];
			if(Num != -1) {
				for(int l = j - 1;l >= 0;--l) if(v[l] == Num) {
					if(max_prev_ind < l) max_prev_ind = l;		
					break;
				}
			}
			assert(max_prev_ind < j);

			for(int i = j - 1;i > max_prev_ind;--i) {
				vi p_ib;
				for(int k = 0;k < i;++k)
					p_ib.pb(v[k]);
				for(int k = j;k >= i;--k)
					p_ib.pb(v[k]);
				for(int k = j + 1;k <= N + 1;++k)
					p_ib.pb(v[k]);		

				Courier C = violate2(p_ib, V.s[K], K);
				if(C < cur_best)
					p_rb = p_ib, cur_best = C;
			}
		}
		if(cur_best < Best) 
			Best = cur_best, v = p_rb;
		else break;
	}
	V.f[K] = v;
	V.s[K] = Best;
}

bool is_update(pc &v, int k, int l, vi &A, vi &B) { //Complexity: O(A.size() + B.size()) <= O(n)
	Courier new_A = violate2(A, v.s[k], k), new_B = violate2(B, v.s[l], l);
	if(new_A.viol + new_B.viol > v.s[k].viol + v.s[l].viol) return false;

	if(new_A.viol + new_B.viol == v.s[k].viol + v.s[l].viol) {
		pdd Old = mp(v.s[k].dist / v.s[k].speed, v.s[l].dist / v.s[l].speed);
		if(Old.f < Old.s) swap(Old.f, Old.s);

		pdd New = mp(new_A.dist / v.s[k].speed, new_B.dist / v.s[l].speed);
		if(New.f < New.s) swap(New.f, New.s);
		if(Old <= New) return false;
	}

	v.f[k] = A, v.f[l] = B;
	v.s[k] = new_A, v.s[l] = new_B;
	return true;
}

bool or_opt(pc &v,int k, int i, int l, int j) { //Complexity: O(v.f[k].size() + v.f[l].size()) <= O(n)
	vi vk = v.f[k], vl = v.f[l];
      int len_k = vk.size(), len_l = vl.size();
	vi A, B;
	for(int t = 0;t <= i;++t)
		A.pb(vk[t]);
	for(int t = j + 1;t < len_l;++t)
		A.pb(vl[t]);

	for(int t = 0;t <= j;++t)
		B.pb(vl[t]);
	for(int t = i + 1;t < len_k;++t)
		B.pb(vk[t]);	

	return is_update(v, k, l, A, B);
}

vi pos_2_opt_exchange(vi &v) { //������ �������, ��� ����� ������ ������. Complexity: O(v.size())
	vi res;
	res.pb(0);
	memset(cur_cnt_comp, 0, (cm + 1) * sizeof(int));
	int len = v.size(), cnt = 0;
	for(int i = 1;i + 1 < len;++i) {
		int j = v[i];
		int n_comp = comp[j];
		if(n_comp == 0) {
			if(cnt == 0) res.pb(i);
			continue;
		}
		cur_cnt_comp[n_comp]++;
		if(cur_cnt_comp[n_comp] == 1) cnt++;
		else if(cur_cnt_comp[n_comp] == cnt_comp[n_comp]) cnt--;
		if(cnt == 0) res.pb(i);
	}
	return res;
}

bool local_search_2_opt_exchange(pc &v) { //Max Complexity: O(n^3)
	memset(calced, 0, c_num * sizeof(bool));
	for(int k = 0;k < c_num;++k) {
		int len1 = v.f[k].size();
		if(len1 < 3) continue;
		if(!calced[k]) {
			lv[k] = pos_2_opt_exchange(v.f[k]);
			calced[k] = true;
		}
		
		for(int l = k + 1;l < c_num;++l) {
			int len2 = v.f[l].size();
			if(len2 < 3) continue;
			if(!calced[l]) {
				lv[l] = pos_2_opt_exchange(v.f[l]);
				calced[l] = true;
			}

			forit(lv[k], it) {
				int i = *it;
				forit(lv[l], it2) {
					int j = *it2;
					if(or_opt(v, k, i, l, j)) return true;
				}
			}
		}
	}
	return false;
}

bool relocate(pc &v, int k, int i, int l, int j) { //Complexity: O(v.f[k].size() + v.f[l].size()) <= O(n)
	vi vk = v.f[k], vl = v.f[l];
      int len_k = vk.size(), len_l = vl.size();
	vi A, B;
	for(int t = 0;t < len_k;++t) if(t != i)
		A.pb(vk[t]);

	for(int t = 0;t < len_l;++t) {
		B.pb(vl[t]);
		if(t == j) B.pb(vk[i]);
	}

	return is_update(v, k, l, A, B);
}

bool local_search_relocate(pc &v) { //Max Complexity: O(n^3)
	for(int k = 0;k < c_num;++k) {
		int len1 = v.f[k].size();
		if(len1 < 3) continue;
		for(int l = 0;l < c_num;++l) if(k != l) {
			int len2 = v.f[l].size();
			for(int i = 1;i + 1 < len1;++i) if(is_can[l][v.f[k][i]]  &&  comp[v.f[k][i]] == 0)
				for(int j = 0;j + 1 < len2;++j) if(relocate(v, k, i, l, j))
					return true;
		}
	}
	return false;
}


bool exchange(pc &v, int k, int i, int l, int j) { //Complexity: O(v.f[k].size() + v.f[l].size()) <= O(n)
	vi vk = v.f[k], vl = v.f[l];
      int len_k = vk.size(), len_l = vl.size();
	vi A, B;

	for(int t = 0;t < len_k;++t) {
		if(t == i) A.pb(vl[j]);
		else A.pb(vk[t]);
	}

	for(int t = 0;t < len_l;++t) {
		if(t == j) B.pb(vk[i]);
		else B.pb(vl[t]);
	}

	return is_update(v, k, l, A, B);
}



bool local_search_exchange(pc &v) { //Max Complexity: O(n^3)
	for(int k = 0;k < c_num;++k) {
		int len1 = v.f[k].size();
		if(len1 < 3) continue;

		for(int l = k + 1;l < c_num;++l) {
			int len2 = v.f[l].size();
			if(len2 < 3) continue;

			for(int i = 1;i + 1 < len1;++i) if(is_can[l][v.f[k][i]]  &&  comp[v.f[k][i]] == 0)
				for(int j = 1;j + 1 < len2;++j) if(is_can[k][v.f[l][j]]  &&  comp[v.f[l][j]] == 0  &&  exchange(v, k, i, l, j))
					return true;
		}
	}
	return false;
}

bool interchange_1_2(pc &v,int k, int i, int l, int j) { //Complexity: O(v.f[k].size() + v.f[l].size()) <= O(n)
	vi vk = v.f[k], vl = v.f[l];
      int len_k = vk.size(), len_l = vl.size();
	vi A, B;

	for(int t = 0;t < len_k;++t) {
		if(t == i) A.pb(vl[j]);
		else if(t != i + 1) A.pb(vk[t]);
	}

	for(int t = 0;t < len_l;++t) {
		if(t == j) {
			B.pb(vk[i]);
			B.pb(vk[i + 1]);
		}
		else B.pb(vl[t]);
	}

	return is_update(v, k, l, A, B);
}


bool local_search_1_2_interchange(pc &v) { //Max Complexity: O(n^3)
	for(int k = 0;k < c_num;++k) {
		int len1 = v.f[k].size();
		if(len1 < 4) continue;

		for(int l = 0;l < c_num;++l) if(k != l) {
			int len2 = v.f[l].size();
			if(len2 < 3) continue;

			for(int i = 1;i + 2 < len1;++i) if(is_can[l][v.f[k][i]]  &&  is_can[l][v.f[k][i + 1]]) {
				int num_comp1 = comp[v.f[k][i]], num_comp2 = comp[v.f[k][i + 1]]; 
				if(num_comp1 != num_comp2) continue;
				if(num_comp1 > 0  &&  cnt_comp[num_comp1] > 2) continue;
				for(int j = 1;j + 1 < len2;++j) if(is_can[k][v.f[l][j]]  &&  comp[v.f[l][j]] == 0  &&  interchange_1_2(v, k, i, l, j))
					return true;
			}
		}
	}
	return false;
}

bool interchange_0_2(pc &v,int k, int i, int l, int j) {  //Complexity: O(v.f[k].size() + v.f[l].size()) <= O(n)
	vi vk = v.f[k], vl = v.f[l];
      int len_k = vk.size(), len_l = vl.size();
	vi A, B;

	for(int t = 0;t < len_k;++t) {
		if(t != i  &&  t != i + 1) A.pb(vk[t]);
	}

	for(int t = 0;t < len_l;++t) {
		B.pb(vl[t]);
		if(t == j) {
			B.pb(vk[i]);
			B.pb(vk[i + 1]);
		}
	}

	return is_update(v, k, l, A, B);
}


bool local_search_0_2_interchange(pc &v) { //Max Complexity: O(n^3)
	for(int k = 0;k < c_num;++k) {
		int len1 = v.f[k].size();
		if(len1 < 4) continue;

		for(int l = 0;l < c_num;++l) if(k != l) {
			int len2 = v.f[l].size();

			for(int i = 1;i + 2 < len1;++i) if(is_can[l][v.f[k][i]]  &&  is_can[l][v.f[k][i + 1]]) {
				int num_comp1 = comp[v.f[k][i]], num_comp2 = comp[v.f[k][i + 1]]; 
				if(num_comp1 != num_comp2) continue;
				if(num_comp1 > 0  &&  cnt_comp[num_comp1] > 2) continue;

				for(int j = 0;j + 1 < len2;++j) if(interchange_0_2(v, k, i, l, j))
					return true;
			}
		}
	}
	return false;
}


bool interchange_2_2(pc &v,int k, int i, int l, int j) { //Complexity: O(v.f[k].size() + v.f[l].size()) <= O(n)
	vi vk = v.f[k], vl = v.f[l];
      int len_k = vk.size(), len_l = vl.size();
	vi A, B;

	for(int t = 0;t < len_k;++t) {
		if(t == i) A.pb(vl[j]);
		else if(t == i + 1) A.pb(vl[j + 1]);
		else A.pb(vk[t]);
	}

	for(int t = 0;t < len_l;++t) {
		if(t == j) B.pb(vk[i]);
		else if(t == j + 1) B.pb(vk[i + 1]);
		else B.pb(vl[t]);
	}

	return is_update(v, k, l, A, B);
}


bool local_search_2_2_interchange(pc &v) { //Max Complexity: O(n^3)
	for(int k = 0;k < c_num;++k) {
		int len1 = v.f[k].size();
		if(len1 < 4) continue;

		for(int l = k + 1;l < c_num;++l) {
			int len2 = v.f[l].size();
			if(len2 < 4) continue;

			for(int i = 1;i + 2 < len1;++i) if(is_can[l][v.f[k][i]]  &&  is_can[l][v.f[k][i + 1]]) {
				int num_comp1 = comp[v.f[k][i]], num_comp2 = comp[v.f[k][i + 1]]; 
				if(num_comp1 != num_comp2) continue;
				if(num_comp1 > 0  &&  cnt_comp[num_comp1] > 2) continue;

				for(int j = 1;j + 2 < len2;++j) if(is_can[k][v.f[l][j]]  &&  is_can[k][v.f[l][j + 1]]) {
					num_comp1 = comp[v.f[l][j]], num_comp2 = comp[v.f[l][j + 1]]; 
					if(num_comp1 != num_comp2) continue;
					if(num_comp1 > 0  &&  cnt_comp[num_comp1] > 2) continue;	

					if(interchange_2_2(v, k, i, l, j)) return true;
				}
			}
		}
	}
	return false;
}

inline void rec(int pos, int last_v, int c_viol, int c_dist, int c_Time) { //Max Complexity: O(c_len * c_len!)
	if(pos == c_len + 1) {
		c_dist += dist[last_v][0];
		c_Time = max(c_Time + Time[c_ind][last_v][0], ord[0].time_ready);
		if(c_Time > ord[0].deadline) c_viol += ord[0].priority;

		if(c_dist <= Dist_lim  &&  c_Time <= fin_time  &&  mp(mp(c_viol, c_dist), c_Time) < Courier_ans) {
			Courier_ans = mp(mp(c_viol, c_dist), c_Time);
			memcpy(ans_path, A, (c_len + 2) * sizeof(int));
		}	
		return;
	}	

	for(int j = 1;j <= c_len;++j) {
		int i = t_arr[j];
		if(used[i]) continue;
		int ind = prev_ind[i];
		if(ind != -1  &&  !used[ind]) continue;

		A[pos] = i;
		used[i] = 1;

		int c_Time2 = max(c_Time + Time[c_ind][last_v][i], ord[i].time_ready), c_viol2 = c_viol;
		if(c_Time2 > ord[i].deadline) c_viol2 += ord[i].priority;
		int c_dist2 = c_dist + dist[last_v][i];

		if(c_dist2 <= Dist_lim  &&  c_Time2 <= fin_time  &&  mp(mp(c_viol2, c_dist2), c_Time2) < Courier_ans)		
			rec(pos + 1, i, c_viol2, c_dist2, c_Time2);

		used[i] = 0;
	}
}

void update_ans(pc &v, int k) { //Max Complexity: O(N * N! + N^3 * max_it_local_search), where N = v.f[k].size() - 2
	c_len = v.f[k].size() - 2, c_ind = k, Dist_lim = v.s[k].dist_limit, fin_time = v.s[k].finish_time;
	assert(Dist_lim == Cr[k].dist_limit  &&  fin_time == Cr[k].finish_time);

	if(c_len <= 8) {
		memset(used, 0, sizeof(used));
		for(int i = 0;i <= c_len;++i) 
			t_arr[i] = v.f[k][i];

		Courier_ans = mp(mp(v.s[k].viol, v.s[k].dist), v.s[k].Time);
		pair <pii, int> cur = Courier_ans;
      	A[0] = A[c_len + 1] = 0;
      	used[0] = 1;
      //	assert(v.s[k].start_time == Cr[k].start_time);
      	rec(1, 0, 0, 0, v.s[k].start_time);

      	if(Courier_ans < cur) {
      		v.f[k].clear();
      		for(int i = 0;i <= c_len + 1;++i)
     			 	v.f[k].pb(ans_path[i]);

     			v.s[k].viol = Courier_ans.f.f, v.s[k].Time = Courier_ans.s, v.s[k].dist = Courier_ans.f.s;
     		}
     		return;
      }
      
      local_search_2_opt(v, k);
      for(int iter = 0;iter < max_it_local_search;++iter) {
      	bool change = false;
      	local_search_1_opt(v, k, change);
      	if(!change) break;
      }
}


pc local_search(pc v) { //Max Complexity: O(n^3 * max_it_local_search)
	assert(v.s.size() == c_num);	

	for(int i = 0;i < c_num;++i) { 
		assert(!v.f[i].empty());
		if(v.f[i].size() == 1) v.f[i].pb(0);
	}
	
 	for(int iter = 0;iter < max_it_local_search;++iter) if(!local_search_1_2_interchange(v))
		break;
		         
 	for(int iter = 0;iter < max_it_local_search;++iter) if(!local_search_2_opt_exchange(v))
		break;

	for(int iter = 0;iter < max_it_local_search;++iter) if(!local_search_relocate(v))
		break;

	for(int iter = 0;iter < max_it_local_search;++iter) if(!local_search_exchange(v))
		break;

	for(int iter = 0;iter < max_it_local_search;++iter) if(!local_search_2_2_interchange(v))
		break;

	for(int iter = 0;iter < max_it_local_search;++iter) if(!local_search_0_2_interchange(v))
		break;
	
	for(int i = 0;i < c_num;++i) {
		if(v.f[i].size() > 3) update_ans(v, i);
		else if(v.f[i].size() == 2) v.f[i].pop_back();
	}
	
	return v;
}        

pc beam_aco() { //Max Complexity: O(Max_it * n^3 * (k_bw * k_ext  * c_num + max_it_local_search))
      double cf = 0;
      bool bs_update = false;
      pc p_bf, p_rb, p_ib;
      pid P_ib = mp(inf, inf);
      pid P_rb = P_ib, P_bf = P_ib;
      init_tau();
      
      for(int iter = 0;iter < Max_it; ++iter) {    
		p_ib = pbs();
		if(p_ib.s.empty()) continue;                  
		p_ib = local_search(p_ib);

		P_ib = violate(p_ib.s); 
		P_rb = violate(p_rb.s);;
		P_bf = violate(p_bf.s);
		if(P_ib < P_rb) 
			p_rb = p_ib, P_rb = P_ib;
		if(P_ib < P_bf) 
			p_bf = p_ib, P_bf = P_ib;
			            
		cf = compute_conv_factor();
		if(bs_update  &&  cf > 0.99) {
			init_tau();
			p_rb.f.clear();
			p_rb.s.clear();
			P_rb = mp(inf, inf);
			bs_update = false;
		}
		else {
			if(cf > 0.99) bs_update = true;
			pheromone_update(cf, bs_update, p_ib.f, p_rb.f, p_bf.f);
		}                            
      }

      return p_bf;
}

void read() { //Complexity: O(n^2)
      scanf("%d%d%d", &is_cycle, &n, &c_num);
      for(int i = 0;i <= n;++i) {
		for(int j = 0;j <= n;++j) 
			scanf("%d", &dist[i][j]);

		if(!is_cycle) dist[i][0] = 0;
		dist[i][i] = inf;
	}

      double _speed;
	for(int i = 0, dist_lim, s_time, f_time;i < c_num;++i) {
		scanf("%lf%d%d%d", &_speed, &dist_lim, &s_time, &f_time);
		Cr[i] = Courier(_speed, dist_lim, 0, 0, s_time, s_time, f_time);
	}

	k_bw = 3 + (n > 50);
	time_l_min = time_r_min = inf;
	time_l_max = time_r_max = -inf;
	memset(next_ind, -1, sizeof(next_ind));

	for(int i = 0, time_l, time_r, prior, serv_time;i <= n;++i)  {
		scanf("%d%d%d%d%d", &time_l, &time_r, &prior, &serv_time, &prev_ind[i]);
		if(prev_ind[i] == 0) prev_ind[i] = -1;
		if(prev_ind[i] != -1) next_ind[prev_ind[i]] = i;

		time_l_min = min(time_l_min, time_l);
		time_l_max = max(time_l_max, time_l);
		time_r_min = min(time_r_min, time_r);
		time_r_max = max(time_r_max, time_r);
		ord[i] = Order(time_l, time_r, prior, serv_time);
	}
	if(!is_cycle) {
		ord[0].deadline = Cr[0].finish_time = inf;
		ord[0].priority = 0;
	}

	for(int j = 0, bb;j < c_num;++j)
		for(int i = 0;i <= n;++i) {
			scanf("%d", &bb);  
			is_can[j][i] = bb;
		}

}

void init_dist_time() { //Complexity: O(n^2 * c_num)
	dist_min = inf, dist_max = -inf;
	for(int i = 0;i <= n;++i) {
		for(int k = 0;k < c_num;++k)
			Time[k][i][i] = inf;

		for(int j = 0;j <= n;++j) if(i != j) {
			dist_min = min(dist_min, dist[i][j]);
			dist_max = max(dist_max, dist[i][j]);

			for(int k = 0;k < c_num;++k) 
				Time[k][i][j] = int(1.0 * dist[i][j] / Cr[k].speed + ord[i].service_time + 0.5);
		}
	}
}

void init_comp() { //Complexity: O(n)
      for(int i = 0;i <= n;++i) if(prev_ind[i] == -1  &&  next_ind[i] != -1) { //for(i = 1;i <= n;++i)
		comp[i] = ++cm;
		cnt_comp[cm] = 1;
		int v = i;
		while(true) {
			v = next_ind[v];
			if(v == -1) break;
			comp[v] = cm;
			cnt_comp[cm]++;
		}
	}
}

void init_can() { //Complexity: O(n * c_num)
      for(int j = 0;j < c_num;++j) 
		for(int i = 1;i <= n;++i) if(!is_can[j][i]) {
			int v = i;
			while(true) {
				v = next_ind[v];
				if(v == -1) break;
				is_can[j][v] = 0;
			}

			v = i;
			while(true) {
				v = prev_ind[v];
				if(v == -1) break;
				is_can[j][v] = 0;
			}
		}

	for(int j = 0;j < c_num;++j) 
		assert(is_can[j][0]);

	for(int i = 1;i <= n;++i) {
		bool found = false;
		for(int j = 0;j < c_num;++j) if(is_can[j][i])
			found = true;
		assert(found);
	}
}

void init_dist_to_depot() { //Complexity: O(n)
	for(int i = 1;i <= n;++i) if(next_ind[i] == -1) {
		dist_to_depot[i] = dist[i][0];
		int from = i, to;
		while(true) {
			to = from;
			from = prev_ind[from];
			if(from == -1) break;

			dist_to_depot[from] = dist_to_depot[to] + dist[from][to];
		}
	}
}

void read_init() {   //read & initialization. Complexity: O(n ^ 2)
//      read();
      /*
      for(int j = 0;j < c_num;++j) {
      	printf("%d: ", j);
      	for(int i = 0;i <= n;++i) if(!is_can[j][i])
      		printf("%d ", i);
      	puts("");
      }
      */
      init_dist_time();           
      init_comp();        
      init_can();      
	init_dist_to_depot();
	calc_nu();
	/*
	cout<<cm<<endl;
	for(int i = 1;i <= cm;++i)
		cout<<cnt_comp[i]<<' ';
	cout<<endl;

	for(int i = 0;i <= n;++i)
		cout<<i<<' '<<comp[i]<<endl; 
	puts("");
	
	
	for(int j = 0;j < c_num;++j) {
		printf("%d: ", j);
      	for(int i = 0;i <= n;++i) if(!is_can[j][i])
      		printf("%d ", i);
      	puts("");
      }

      cout<<endl;
      */
}

void print(pid P, vvi &V, vector <Courier> vc) { //print answer. Complexity: O(n)

	int i = 0, total_dist = 0;
	forit(V, it) {
		vi v = *it;
		assert(v.back() == 0);
		if(!is_cycle  &&  v.size() > 1) v.pop_back();
	//	if(v.back() != 0) v.pb(0);
		forit(v, it2)
			printf("%d ", *it2);
		puts("");
		Courier c = vc[i];
		total_dist += c.dist;
		printf("%d %d %d\n", c.dist, c.viol, c.Time);
		/*
		if(v.back() != 0) v.pb(0);
		Courier C = violate2(v, Cr[i], i);
		printf("speed = %.2lf dist_limit = %d dist = %d viol = %d time = %d\n", C.speed, C.dist_limit, C.dist, C.viol, C.Time);
		*/
		++i;
		puts("");
	}
    printf("%d %.6lf %d", P.f, P.s, total_dist);
//	printf("\n%d\n", total_dist);
}

void solve() { //Max Complexity: O(cnt_iter * Max_it * n^3 * (k_bw * k_ext  * c_num + max_it_local_search))
      read_init();
      pc res;
      //res.clear();
      pid P = mp(inf, inf);
      for(int iter = 0;iter < cnt_iter; ++iter) {
		pc V = beam_aco(); 
		pid cur = violate(V.s);
		if(P > cur) {
			res = V;
			P = cur;
		}
	} 
	print(P, res.f, res.s);
}

void import_distance_matrix(char* distances_string){
    size_t pos = 0;
    size_t pos_inner = 0;
    int i = 0;
    int j = 0;
    std::string token;
    std::string s = distances_string;
    std::string c;

    while ((pos = s.find(";")) != std::string::npos) {
        token = s.substr(0, pos);

        j = 0;
        while ((pos_inner = token.find(",")) != std::string::npos) {
            c = token.substr(0, pos_inner);

            token.erase(0, pos_inner + 1);
            dist[i][j] = std::stoi(c);
            j+=1;
        }
        dist[i][j] = std::stoi(token);
        if(!is_cycle) dist[i][0] = 0;
		dist[i][i] = inf;
        s.erase(0, pos + 1);
        i += 1;
    }
    token = s;
    j = 0;
    while ((pos_inner = token.find(",")) != std::string::npos) {
        c = token.substr(0, pos_inner);

        token.erase(0, pos_inner + 1);
        dist[i][j] = std::stoi(c);
        j+=1;
    }
    dist[i][j] = std::stoi(token);
    if(!is_cycle) dist[i][0] = 0;
    dist[i][i] = inf;

//    printf("\n");
//    for(int i = 0;i <= n;++i) {
//		for(int j = 0;j <= n;++j)
//			printf("%d ", dist[i][j]);
//
//		printf("\n");
//	}
}

void import_couriers_info(char* couriers_info_string){
    size_t pos = 0;
    size_t pos_inner = 0;
    int i = 0;
    int j = 0;
    std::string token;
    std::string s = couriers_info_string;
    std::string c;
    double speed;
    int dist_lim, s_time, f_time;

    while ((pos = s.find(";")) != std::string::npos) {
        token = s.substr(0, pos);
        j = 0;
        while ((pos_inner = token.find(",")) != std::string::npos) {
            c = token.substr(0, pos_inner);

            token.erase(0, pos_inner + 1);
            if (j == 0){
                speed = std::stod(c);
            }
            if (j == 1){
                dist_lim = std::stoi(c);
            }
            if (j == 2){
                s_time = std::stoi(c);
            }
            j+=1;
        }
        f_time = std::stoi(token);
        Cr[i] = Courier(speed, dist_lim, 0, 0, s_time, s_time, f_time);

        s.erase(0, pos + 1);
        i += 1;
    }
    token = s;
    j = 0;
    while ((pos_inner = token.find(",")) != std::string::npos) {
        c = token.substr(0, pos_inner);

        token.erase(0, pos_inner + 1);
        if (j == 0){
            speed = std::stod(c);
        }
        if (j == 1){
            dist_lim = std::stoi(c);
        }
        if (j == 2){
            s_time = std::stoi(c);
        }
        j+=1;
    }
    f_time = std::stoi(token);

    Cr[i] = Courier(speed, dist_lim, 0, 0, s_time, s_time, f_time);

    k_bw = 3 + (n > 50);
	time_l_min = time_r_min = inf;
	time_l_max = time_r_max = -inf;
	memset(next_ind, -1, sizeof(next_ind));
//    printf("%d %d\n", i, j);

//    printf("\n");
//    for(int i = 0;i <= c_num;++i) {
//		printf("%.6lf %d %d %d", Cr[i].speed,Cr[i].dist_limit,Cr[i].start_time,Cr[i].finish_time );
//
//		printf("\n");
//	}
}

void import_orders_info(char* orders_info_string){
    size_t pos = 0;
    size_t pos_inner = 0;
    int i = 0;
    int j = 0;
    std::string token;
    std::string s = orders_info_string;
    std::string c;
    int time_l, time_r, prior, serv_time;

    while ((pos = s.find(";")) != std::string::npos) {
        token = s.substr(0, pos);
        j = 0;
        while ((pos_inner = token.find(",")) != std::string::npos) {
            c = token.substr(0, pos_inner);

            token.erase(0, pos_inner + 1);
            if (j == 0){
                time_l = std::stoi(c);
            }
            if (j == 1){
                time_r = std::stoi(c);
            }
            if (j == 2){
                prior = std::stoi(c);
            }
            if (j == 3){
                serv_time = std::stoi(c);
            }
            j+=1;
        }
        prev_ind[i] = std::stoi(token);
        if(prev_ind[i] == 0) prev_ind[i] = -1;
		if(prev_ind[i] != -1) next_ind[prev_ind[i]] = i;
		time_l_min = min(time_l_min, time_l);
		time_l_max = max(time_l_max, time_l);
		time_r_min = min(time_r_min, time_r);
		time_r_max = max(time_r_max, time_r);

        ord[i] = Order(time_l, time_r, prior, serv_time);

        s.erase(0, pos + 1);
        i += 1;
    }
    token = s.substr(0, pos);
    j = 0;
    while ((pos_inner = token.find(",")) != std::string::npos) {
        c = token.substr(0, pos_inner);

        token.erase(0, pos_inner + 1);
        if (j == 0){
            time_l = std::stoi(c);
        }
        if (j == 1){
            time_r = std::stoi(c);
        }
        if (j == 2){
            prior = std::stoi(c);
        }
        if (j == 3){
            serv_time = std::stoi(c);
        }
        j+=1;
    }
    prev_ind[i] = std::stoi(token);
    if(prev_ind[i] == 0) prev_ind[i] = -1;
    if(prev_ind[i] != -1) next_ind[prev_ind[i]] = i;
    time_l_min = min(time_l_min, time_l);
    time_l_max = max(time_l_max, time_l);
    time_r_min = min(time_r_min, time_r);
    time_r_max = max(time_r_max, time_r);

    ord[i] = Order(time_l, time_r, prior, serv_time);

    if (!is_cycle){
//        printf("----IN CYCLE-----");
        ord[0].deadline = Cr[0].finish_time = inf;
		ord[0].priority = 0;
    } else {
//        printf("----NOT IN CYCLE-----");
    }
//    printf("%d %d\n", i, j);
//    printf("\n");
//    for(int i = 0;i <= n;++i) {
//        printf("%d %d %d %d %d", ord[i].time_ready,ord[i].deadline,ord[i].priority,ord[i].service_time, prev_ind[i]);
////		printf("%d ", prev_ind[i]);
//
//		printf("\n");
//	}
}

void import_can_deliver_matrix(char* can_deliver_string){
    size_t pos = 0;
    size_t pos_inner = 0;
    int i = 0;
    int j = 0;
    std::string token;
    std::string s = can_deliver_string;
    std::string c;

    while ((pos = s.find(";")) != std::string::npos) {
        token = s.substr(0, pos);
        j = 0;
        while ((pos_inner = token.find(",")) != std::string::npos) {
            c = token.substr(0, pos_inner);

            token.erase(0, pos_inner + 1);
            is_can[i][j] = std::stoi(c);
            j+=1;
        }
        is_can[i][j] = std::stoi(c);

        s.erase(0, pos + 1);
        i += 1;
    }
    token = s.substr(0, pos);
    j = 0;
    while ((pos_inner = token.find(",")) != std::string::npos) {
        c = token.substr(0, pos_inner);

        token.erase(0, pos_inner + 1);
        is_can[i][j] = std::stoi(c);
        j+=1;
    }
    is_can[i][j] = std::stoi(c);
//    printf("%d %d", i, j);
    s.erase(0, pos + 1);
    i += 1;
//    printf("\n");
//    for(int i = 0;i < c_num;++i) {
//		for(int j = 0;j <= n;++j)
//			printf("%d ", is_can[j][i]);
//
//		printf("\n");
//	}
}

int main (int argc, char *argv[]) {
    is_cycle = std::stoi(argv[1]);
    n = std::stoi(argv[2]);
    c_num = std::stoi(argv[3]);

    char* distance_matrix = argv[4];
    char* couriers_info = argv[5];
    char* orders_info = argv[6];
    char* courier_can_deliver_matrix = argv[7];
	// is_cycle, n, c_num
	// distance_matrix
	// courier_info
	// orders_info
	// courier_can_deliver info
//	printf("Before import");
	import_distance_matrix(distance_matrix);
//	printf("After import distance_matrix");
	import_couriers_info(couriers_info);
//	printf("After import couriers_info");
	import_orders_info(orders_info);
//	printf("After import orders_info");
	import_can_deliver_matrix(courier_can_deliver_matrix);
//	printf("After import all");

//	printf("\n");
//        for(int i = 0;i <= n;++i) {
//            for(int j = 0;j <= n;++j)
//                printf("%d ", dist[i][j]);
//
//            printf("\n");
//        }
//      printf("\n");
//        for(int i = 0;i <= c_num;++i) {
//            printf("%.6lf %d %d %d", Cr[i].speed,Cr[i].dist_limit,Cr[i].start_time,Cr[i].finish_time );
//
//            printf("\n");
//        }
//        printf("\n");
//    for(int i = 0;i <= n+1;++i) {
//        printf("%d %d %d %d %d", ord[i].time_ready,ord[i].deadline,ord[i].priority,ord[i].service_time, prev_ind[i]);
////		printf("%d ", prev_ind[i]);
//
//		printf("\n");
//	}
//	printf("\n");
//    for(int i = 0;i < c_num;++i) {
//		for(int j = 0;j <= n;++j)
//			printf("%d ", is_can[j][i]);
//
//		printf("\n");
//	}

	srand(time(0));
	double TT = clock();
	solve();


	cerr<<(clock() - TT) / 1000;
	
	return 0;
}